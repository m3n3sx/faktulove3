#!/usr/bin/env python3
"""
Training Data Collector for OCR Model Improvement
Automated collection of high-quality training data with privacy protection
"""

import os
import json
import logging
import hashlib
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import shutil
import zipfile
import csv

# Django imports
try:
    from django.conf import settings
    from django.core.cache import cache
    from django.db.models import Q, Count, Avg
    from django.utils import timezone
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    settings = None

logger = logging.getLogger(__name__)


@dataclass
class TrainingSample:
    """Represents a training data sample"""
    sample_id: str
    original_text: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    human_rating: Optional[int] = None
    human_corrections: Optional[Dict[str, Any]] = None
    collection_date: datetime = None
    anonymized: bool = False
    quality_score: float = 0.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.collection_date is None:
            self.collection_date = timezone.now() if DJANGO_AVAILABLE else datetime.now()
        if self.tags is None:
            self.tags = []


@dataclass
class CollectionMetrics:
    """Metrics for data collection"""
    total_samples: int
    high_quality_samples: int
    human_validated_samples: int
    average_confidence: float
    average_human_rating: float
    collection_rate_per_day: float
    privacy_compliance_score: float
    data_quality_score: float


class PrivacyProtector:
    """Handles privacy protection for training data"""
    
    def __init__(self):
        self.sensitive_patterns = [
            r'\b\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}\b',  # NIP
            r'\b\d{9}\b',  # REGON
            r'\b\d{14}\b',  # REGON 14-digit
            r'\b\d{10}\b',  # KRS
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b(\+\d{2}\s+\d{3}\s+\d{3}\s+\d{3})\b',  # Phone
            r'\b(\d{2}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4})\b',  # Bank account
        ]
        
        self.replacement_map = {
            'nip': '[NIP_MASKED]',
            'regon': '[REGON_MASKED]',
            'krs': '[KRS_MASKED]',
            'email': '[EMAIL_MASKED]',
            'phone': '[PHONE_MASKED]',
            'bank_account': '[BANK_ACCOUNT_MASKED]',
            'company_name': '[COMPANY_MASKED]',
            'address': '[ADDRESS_MASKED]'
        }
    
    def anonymize_text(self, text: str) -> str:
        """Anonymize sensitive information in text"""
        import re
        
        anonymized_text = text
        
        # Replace NIP numbers
        anonymized_text = re.sub(
            r'\b\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}\b',
            '[NIP_MASKED]',
            anonymized_text
        )
        
        # Replace REGON numbers
        anonymized_text = re.sub(r'\b\d{9}\b', '[REGON_MASKED]', anonymized_text)
        anonymized_text = re.sub(r'\b\d{14}\b', '[REGON_MASKED]', anonymized_text)
        
        # Replace KRS numbers
        anonymized_text = re.sub(r'\b\d{10}\b', '[KRS_MASKED]', anonymized_text)
        
        # Replace email addresses
        anonymized_text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_MASKED]',
            anonymized_text
        )
        
        # Replace phone numbers
        anonymized_text = re.sub(
            r'\b(\+\d{2}\s+\d{3}\s+\d{3}\s+\d{3})\b',
            '[PHONE_MASKED]',
            anonymized_text
        )
        
        # Replace bank account numbers
        anonymized_text = re.sub(
            r'\b(\d{2}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4})\b',
            '[BANK_ACCOUNT_MASKED]',
            anonymized_text
        )
        
        return anonymized_text
    
    def anonymize_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive information in extracted data"""
        anonymized_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Check if the field contains sensitive data
                if any(pattern in key.lower() for pattern in ['nip', 'regon', 'krs', 'email', 'phone']):
                    anonymized_data[key] = f'[{key.upper()}_MASKED]'
                elif 'company' in key.lower() or 'nazwa' in key.lower():
                    anonymized_data[key] = '[COMPANY_MASKED]'
                elif 'address' in key.lower() or 'adres' in key.lower():
                    anonymized_data[key] = '[ADDRESS_MASKED]'
                else:
                    anonymized_data[key] = value
            elif isinstance(value, dict):
                anonymized_data[key] = self.anonymize_extracted_data(value)
            elif isinstance(value, list):
                anonymized_data[key] = [
                    self.anonymize_extracted_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                anonymized_data[key] = value
        
        return anonymized_data
    
    def calculate_privacy_score(self, text: str, data: Dict[str, Any]) -> float:
        """Calculate privacy compliance score"""
        import re
        
        score = 1.0
        sensitive_count = 0
        
        # Count sensitive patterns in text
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, text)
            sensitive_count += len(matches)
        
        # Count sensitive fields in extracted data
        sensitive_fields = ['nip', 'regon', 'krs', 'email', 'phone', 'bank_account']
        for field in sensitive_fields:
            if any(field in key.lower() for key in data.keys()):
                sensitive_count += 1
        
        # Reduce score based on sensitive data presence
        if sensitive_count > 0:
            score = max(0.0, 1.0 - (sensitive_count * 0.1))
        
        return score


class TrainingDataCollector:
    """
    Training Data Collector for continuous model improvement
    Collects high-quality OCR results for model training
    """
    
    def __init__(self, 
                 collection_dir: str = "training_data",
                 min_confidence_threshold: float = 95.0,
                 min_human_rating: int = 8,
                 max_samples_per_day: int = 1000,
                 privacy_enabled: bool = True):
        """
        Initialize training data collector
        
        Args:
            collection_dir: Directory to store training data
            min_confidence_threshold: Minimum confidence for high-quality samples
            min_human_rating: Minimum human rating for validated samples
            max_samples_per_day: Maximum samples to collect per day
            privacy_enabled: Enable privacy protection
        """
        self.collection_dir = Path(collection_dir)
        self.min_confidence_threshold = min_confidence_threshold
        self.min_human_rating = min_human_rating
        self.max_samples_per_day = max_samples_per_day
        self.privacy_enabled = privacy_enabled
        
        # Create directories
        self.collection_dir.mkdir(parents=True, exist_ok=True)
        (self.collection_dir / "high_confidence").mkdir(exist_ok=True)
        (self.collection_dir / "human_validated").mkdir(exist_ok=True)
        (self.collection_dir / "exports").mkdir(exist_ok=True)
        (self.collection_dir / "metrics").mkdir(exist_ok=True)
        
        # Initialize privacy protector
        self.privacy_protector = PrivacyProtector() if privacy_enabled else None
        
        # Collection statistics
        self.collection_stats = {
            'total_collected': 0,
            'high_confidence_collected': 0,
            'human_validated_collected': 0,
            'privacy_violations': 0,
            'last_collection_date': None
        }
        
        logger.info(f"Training Data Collector initialized with threshold {min_confidence_threshold}%")
    
    def collect_high_confidence_results(self, 
                                      ocr_results: List[Dict[str, Any]], 
                                      confidence_threshold: float = None) -> List[TrainingSample]:
        """
        Collect high-confidence OCR results for training
        
        Args:
            ocr_results: List of OCR processing results
            confidence_threshold: Override default confidence threshold
            
        Returns:
            List of collected training samples
        """
        if confidence_threshold is None:
            confidence_threshold = self.min_confidence_threshold
        
        collected_samples = []
        
        for result in ocr_results:
            try:
                confidence = result.get('confidence_score', 0.0)
                
                # Check if result meets confidence threshold
                if confidence >= confidence_threshold:
                    # Create training sample
                    sample = self._create_training_sample(result, 'high_confidence')
                    
                    # Apply privacy protection if enabled
                    if self.privacy_enabled:
                        sample.original_text = self.privacy_protector.anonymize_text(sample.original_text)
                        sample.extracted_data = self.privacy_protector.anonymize_extracted_data(sample.extracted_data)
                        sample.anonymized = True
                        sample.quality_score = self.privacy_protector.calculate_privacy_score(
                            sample.original_text, sample.extracted_data
                        )
                    
                    # Save sample
                    self._save_training_sample(sample, 'high_confidence')
                    collected_samples.append(sample)
                    
                    # Update statistics
                    self.collection_stats['high_confidence_collected'] += 1
                    self.collection_stats['total_collected'] += 1
                    
                    logger.info(f"Collected high-confidence sample {sample.sample_id} with confidence {confidence:.2f}%")
                
            except Exception as e:
                logger.error(f"Error collecting high-confidence result: {e}")
                continue
        
        self.collection_stats['last_collection_date'] = timezone.now() if DJANGO_AVAILABLE else datetime.now()
        return collected_samples
    
    def collect_human_validated_results(self, 
                                      validated_results: List[Dict[str, Any]], 
                                      min_rating: int = None) -> List[TrainingSample]:
        """
        Collect human-validated OCR results
        
        Args:
            validated_results: List of human-validated results
            min_rating: Override default minimum rating
            
        Returns:
            List of collected training samples
        """
        if min_rating is None:
            min_rating = self.min_human_rating
        
        collected_samples = []
        
        for result in validated_results:
            try:
                human_rating = result.get('human_rating', 0)
                
                # Check if result meets minimum rating
                if human_rating >= min_rating:
                    # Create training sample
                    sample = self._create_training_sample(result, 'human_validated')
                    sample.human_rating = human_rating
                    sample.human_corrections = result.get('human_corrections', {})
                    
                    # Apply privacy protection if enabled
                    if self.privacy_enabled:
                        sample.original_text = self.privacy_protector.anonymize_text(sample.original_text)
                        sample.extracted_data = self.privacy_protector.anonymize_extracted_data(sample.extracted_data)
                        sample.anonymized = True
                        sample.quality_score = self.privacy_protector.calculate_privacy_score(
                            sample.original_text, sample.extracted_data
                        )
                    
                    # Save sample
                    self._save_training_sample(sample, 'human_validated')
                    collected_samples.append(sample)
                    
                    # Update statistics
                    self.collection_stats['human_validated_collected'] += 1
                    self.collection_stats['total_collected'] += 1
                    
                    logger.info(f"Collected human-validated sample {sample.sample_id} with rating {human_rating}")
                
            except Exception as e:
                logger.error(f"Error collecting human-validated result: {e}")
                continue
        
        self.collection_stats['last_collection_date'] = timezone.now() if DJANGO_AVAILABLE else datetime.now()
        return collected_samples
    
    def export_training_dataset(self, 
                               format: str = 'document_ai',
                               include_high_confidence: bool = True,
                               include_human_validated: bool = True,
                               output_file: str = None) -> str:
        """
        Export training dataset in various formats
        
        Args:
            format: Export format ('document_ai', 'paddleocr', 'easyocr', 'json', 'csv')
            include_high_confidence: Include high-confidence samples
            include_human_validated: Include human-validated samples
            output_file: Output file path (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        try:
            # Collect all samples
            all_samples = []
            
            if include_high_confidence:
                high_confidence_samples = self._load_training_samples('high_confidence')
                all_samples.extend(high_confidence_samples)
            
            if include_human_validated:
                human_validated_samples = self._load_training_samples('human_validated')
                all_samples.extend(human_validated_samples)
            
            if not all_samples:
                logger.warning("No training samples found for export")
                return None
            
            # Generate output filename if not provided
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"training_dataset_{format}_{timestamp}"
            
            output_path = self.collection_dir / "exports" / output_file
            
            # Export based on format
            if format == 'document_ai':
                return self._export_document_ai_format(all_samples, output_path)
            elif format == 'paddleocr':
                return self._export_paddleocr_format(all_samples, output_path)
            elif format == 'easyocr':
                return self._export_easyocr_format(all_samples, output_path)
            elif format == 'json':
                return self._export_json_format(all_samples, output_path)
            elif format == 'csv':
                return self._export_csv_format(all_samples, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting training dataset: {e}")
            return None
    
    def get_collection_metrics(self) -> CollectionMetrics:
        """Get collection metrics and statistics"""
        try:
            # Calculate daily collection rate
            if self.collection_stats['last_collection_date']:
                days_since_last = (timezone.now() - self.collection_stats['last_collection_date']).days
                collection_rate = self.collection_stats['total_collected'] / max(days_since_last, 1)
            else:
                collection_rate = 0.0
            
            # Calculate average confidence and ratings
            high_confidence_samples = self._load_training_samples('high_confidence')
            human_validated_samples = self._load_training_samples('human_validated')
            
            avg_confidence = 0.0
            if high_confidence_samples:
                avg_confidence = sum(s.confidence_score for s in high_confidence_samples) / len(high_confidence_samples)
            
            avg_human_rating = 0.0
            if human_validated_samples:
                rated_samples = [s for s in human_validated_samples if s.human_rating is not None]
                if rated_samples:
                    avg_human_rating = sum(s.human_rating for s in rated_samples) / len(rated_samples)
            
            # Calculate privacy compliance score
            privacy_score = 1.0
            if self.privacy_enabled and self.collection_stats['privacy_violations'] > 0:
                privacy_score = max(0.0, 1.0 - (self.collection_stats['privacy_violations'] / self.collection_stats['total_collected']))
            
            # Calculate data quality score
            quality_scores = [s.quality_score for s in high_confidence_samples + human_validated_samples]
            data_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            return CollectionMetrics(
                total_samples=self.collection_stats['total_collected'],
                high_quality_samples=self.collection_stats['high_confidence_collected'],
                human_validated_samples=self.collection_stats['human_validated_collected'],
                average_confidence=avg_confidence,
                average_human_rating=avg_human_rating,
                collection_rate_per_day=collection_rate,
                privacy_compliance_score=privacy_score,
                data_quality_score=data_quality_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating collection metrics: {e}")
            return CollectionMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    def cleanup_old_samples(self, days_to_keep: int = 90) -> int:
        """
        Clean up old training samples
        
        Args:
            days_to_keep: Number of days to keep samples
            
        Returns:
            Number of samples removed
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_to_keep) if DJANGO_AVAILABLE else datetime.now() - timedelta(days=days_to_keep)
            removed_count = 0
            
            # Clean up high confidence samples
            high_confidence_dir = self.collection_dir / "high_confidence"
            if high_confidence_dir.exists():
                for sample_file in high_confidence_dir.glob("*.json"):
                    if sample_file.stat().st_mtime < cutoff_date.timestamp():
                        sample_file.unlink()
                        removed_count += 1
            
            # Clean up human validated samples
            human_validated_dir = self.collection_dir / "human_validated"
            if human_validated_dir.exists():
                for sample_file in human_validated_dir.glob("*.json"):
                    if sample_file.stat().st_mtime < cutoff_date.timestamp():
                        sample_file.unlink()
                        removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old training samples")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old samples: {e}")
            return 0
    
    def _create_training_sample(self, result: Dict[str, Any], sample_type: str) -> TrainingSample:
        """Create a training sample from OCR result"""
        sample_id = self._generate_sample_id(result)
        
        return TrainingSample(
            sample_id=sample_id,
            original_text=result.get('raw_text', ''),
            extracted_data=result.get('extracted_data', {}),
            confidence_score=result.get('confidence_score', 0.0),
            tags=[sample_type, f"confidence_{int(result.get('confidence_score', 0))}"]
        )
    
    def _generate_sample_id(self, result: Dict[str, Any]) -> str:
        """Generate unique sample ID"""
        content_hash = hashlib.md5(
            (result.get('raw_text', '') + str(result.get('extracted_data', {}))).encode()
        ).hexdigest()[:8]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"sample_{timestamp}_{content_hash}"
    
    def _save_training_sample(self, sample: TrainingSample, sample_type: str):
        """Save training sample to file"""
        sample_dir = self.collection_dir / sample_type
        sample_file = sample_dir / f"{sample.sample_id}.json"
        
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(sample), f, indent=2, default=str)
    
    def _load_training_samples(self, sample_type: str) -> List[TrainingSample]:
        """Load training samples from files"""
        samples = []
        sample_dir = self.collection_dir / sample_type
        
        if not sample_dir.exists():
            return samples
        
        for sample_file in sample_dir.glob("*.json"):
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    sample_data = json.load(f)
                    sample = TrainingSample(**sample_data)
                    samples.append(sample)
            except Exception as e:
                logger.error(f"Error loading sample {sample_file}: {e}")
                continue
        
        return samples
    
    def _export_document_ai_format(self, samples: List[TrainingSample], output_path: Path) -> str:
        """Export in Google Document AI format"""
        output_file = output_path.with_suffix('.json')
        
        document_ai_data = {
            'training_data': [],
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_samples': len(samples),
                'format': 'document_ai'
            }
        }
        
        for sample in samples:
            doc_ai_sample = {
                'id': sample.sample_id,
                'text': sample.original_text,
                'entities': self._convert_to_document_ai_entities(sample.extracted_data),
                'confidence': sample.confidence_score,
                'human_rating': sample.human_rating,
                'corrections': sample.human_corrections
            }
            document_ai_data['training_data'].append(doc_ai_sample)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(document_ai_data, f, indent=2)
        
        return str(output_file)
    
    def _export_paddleocr_format(self, samples: List[TrainingSample], output_path: Path) -> str:
        """Export in PaddleOCR format"""
        output_file = output_path.with_suffix('.json')
        
        paddleocr_data = {
            'training_samples': [],
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_samples': len(samples),
                'format': 'paddleocr'
            }
        }
        
        for sample in samples:
            paddle_sample = {
                'sample_id': sample.sample_id,
                'text': sample.original_text,
                'extracted_fields': sample.extracted_data,
                'confidence': sample.confidence_score,
                'quality_score': sample.quality_score,
                'tags': sample.tags
            }
            paddleocr_data['training_samples'].append(paddle_sample)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(paddleocr_data, f, indent=2)
        
        return str(output_file)
    
    def _export_easyocr_format(self, samples: List[TrainingSample], output_path: Path) -> str:
        """Export in EasyOCR format"""
        output_file = output_path.with_suffix('.json')
        
        easyocr_data = {
            'training_data': [],
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_samples': len(samples),
                'format': 'easyocr'
            }
        }
        
        for sample in samples:
            easy_sample = {
                'id': sample.sample_id,
                'text': sample.original_text,
                'extracted_data': sample.extracted_data,
                'confidence': sample.confidence_score,
                'human_validation': {
                    'rating': sample.human_rating,
                    'corrections': sample.human_corrections
                }
            }
            easyocr_data['training_data'].append(easy_sample)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(easyocr_data, f, indent=2)
        
        return str(output_file)
    
    def _export_json_format(self, samples: List[TrainingSample], output_path: Path) -> str:
        """Export in generic JSON format"""
        output_file = output_path.with_suffix('.json')
        
        json_data = {
            'samples': [asdict(sample) for sample in samples],
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_samples': len(samples),
                'format': 'json'
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        return str(output_file)
    
    def _export_csv_format(self, samples: List[TrainingSample], output_path: Path) -> str:
        """Export in CSV format"""
        output_file = output_path.with_suffix('.csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'sample_id', 'original_text', 'confidence_score', 'human_rating',
                'quality_score', 'anonymized', 'collection_date', 'tags'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for sample in samples:
                writer.writerow({
                    'sample_id': sample.sample_id,
                    'original_text': sample.original_text[:1000],  # Limit text length
                    'confidence_score': sample.confidence_score,
                    'human_rating': sample.human_rating or '',
                    'quality_score': sample.quality_score,
                    'anonymized': sample.anonymized,
                    'collection_date': sample.collection_date.isoformat() if sample.collection_date else '',
                    'tags': ','.join(sample.tags) if sample.tags else ''
                })
        
        return str(output_file)
    
    def _convert_to_document_ai_entities(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert extracted data to Document AI entity format"""
        entities = []
        
        for field_name, field_value in extracted_data.items():
            if isinstance(field_value, str) and field_value:
                entity = {
                    'type': field_name,
                    'mention_text': field_value,
                    'confidence': 0.95,  # Default confidence
                    'page_anchor': {
                        'page_refs': [{'page': 1}]
                    }
                }
                entities.append(entity)
        
        return entities
