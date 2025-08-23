"""
Training Dataset Manager for Polish Invoice OCR Custom Training
"""

import json
import logging
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from faktury.models import DocumentUpload, OCRResult, OCRValidation

logger = logging.getLogger(__name__)


class TrainingDatasetManager:
    """
    Manages training datasets for custom model training with Google Document AI
    """
    
    def __init__(self):
        self.dataset_path = getattr(settings, 'OCR_TRAINING_DATASET_PATH', 'training_data/')
        self.min_confidence_threshold = 95.0
        self.min_validation_score = 8  # Out of 10
        
    def collect_training_data(self, limit: int = 1000) -> Dict[str, Any]:
        """
        Collect high-quality OCR results for training dataset
        
        Args:
            limit: Maximum number of documents to include
            
        Returns:
            Dictionary with training data statistics and file paths
        """
        logger.info(f"Collecting training data with limit: {limit}")
        
        # Get high-confidence, validated OCR results
        high_quality_results = OCRResult.objects.filter(
            confidence_score__gte=self.min_confidence_threshold,
            ocrvalidation__accuracy_rating__gte=self.min_validation_score
        ).select_related('document', 'ocrvalidation').order_by('-confidence_score')[:limit]
        
        training_samples = []
        annotation_data = []
        
        for ocr_result in high_quality_results:
            try:
                # Prepare training sample
                sample = self._prepare_training_sample(ocr_result)
                if sample:
                    training_samples.append(sample)
                    
                    # Prepare annotation data for Document AI
                    annotation = self._prepare_document_ai_annotation(ocr_result)
                    if annotation:
                        annotation_data.append(annotation)
                        
            except Exception as e:
                logger.error(f"Error preparing training sample for OCR result {ocr_result.id}: {e}")
                continue
        
        # Save training dataset
        dataset_info = self._save_training_dataset(training_samples, annotation_data)
        
        logger.info(f"Collected {len(training_samples)} training samples")
        
        return {
            'total_samples': len(training_samples),
            'dataset_path': dataset_info['dataset_path'],
            'annotation_path': dataset_info['annotation_path'],
            'statistics': self._calculate_dataset_statistics(training_samples),
            'document_ai_config': self._generate_document_ai_config(annotation_data)
        }
    
    def _prepare_training_sample(self, ocr_result: OCRResult) -> Dict[str, Any]:
        """Prepare a single training sample from OCR result"""
        
        document = ocr_result.document
        validation = getattr(ocr_result, 'ocrvalidation', None)
        
        if not validation:
            return None
        
        # Get corrected data from validation
        corrected_data = validation.corrected_data or ocr_result.extracted_data
        
        sample = {
            'document_id': document.id,
            'file_path': document.file_path,
            'original_filename': document.original_filename,
            'confidence_score': ocr_result.confidence_score,
            'validation_score': validation.accuracy_rating,
            'raw_text': ocr_result.raw_text,
            'extracted_data': corrected_data,
            'ground_truth': self._prepare_ground_truth(corrected_data),
            'metadata': {
                'upload_date': document.upload_timestamp.isoformat(),
                'validation_date': validation.validation_timestamp.isoformat(),
                'file_size': document.file_size,
                'content_type': document.content_type,
                'processing_time': ocr_result.processing_time,
                'processor_version': ocr_result.processor_version
            }
        }
        
        return sample
    
    def _prepare_ground_truth(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare ground truth labels for training"""
        
        # Map our field names to Document AI entity types
        field_mapping = {
            'invoice_number': 'invoice_id',
            'invoice_date': 'invoice_date',
            'due_date': 'due_date',
            'supplier_name': 'supplier_name',
            'supplier_nip': 'supplier_tax_id',
            'supplier_address': 'supplier_address',
            'buyer_name': 'receiver_name',
            'buyer_nip': 'receiver_tax_id',
            'buyer_address': 'receiver_address',
            'total_amount': 'total_amount',
            'net_amount': 'net_amount',
            'vat_amount': 'vat_amount',
            'currency': 'currency'
        }
        
        ground_truth = {}
        
        for our_field, doc_ai_field in field_mapping.items():
            if our_field in extracted_data and extracted_data[our_field]:
                ground_truth[doc_ai_field] = {
                    'value': str(extracted_data[our_field]),
                    'confidence': 1.0,  # Ground truth has 100% confidence
                    'source': 'human_validated'
                }
        
        # Add line items if present
        if 'line_items' in extracted_data and extracted_data['line_items']:
            ground_truth['line_items'] = []
            for item in extracted_data['line_items']:
                ground_truth_item = {}
                if 'description' in item:
                    ground_truth_item['line_item_description'] = item['description']
                if 'quantity' in item:
                    ground_truth_item['line_item_quantity'] = str(item['quantity'])
                if 'unit_price' in item:
                    ground_truth_item['line_item_unit_price'] = str(item['unit_price'])
                if 'vat_rate' in item:
                    ground_truth_item['line_item_vat_rate'] = str(item['vat_rate'])
                
                if ground_truth_item:
                    ground_truth['line_items'].append(ground_truth_item)
        
        return ground_truth
    
    def _prepare_document_ai_annotation(self, ocr_result: OCRResult) -> Dict[str, Any]:
        """Prepare annotation data for Document AI custom training"""
        
        document = ocr_result.document
        ground_truth = self._prepare_ground_truth(ocr_result.extracted_data)
        
        # Document AI annotation format
        annotation = {
            'display_name': f"invoice_{document.id}",
            'document': {
                'uri': f"gs://faktulove-ocr-training/{document.original_filename}",
                'mime_type': document.content_type
            },
            'entities': []
        }
        
        # Convert ground truth to Document AI entities
        for field_name, field_data in ground_truth.items():
            if field_name != 'line_items' and isinstance(field_data, dict):
                entity = {
                    'type': field_name,
                    'mention_text': field_data['value'],
                    'confidence': field_data['confidence'],
                    'text_anchor': {
                        'content': field_data['value']
                        # Note: In real implementation, you'd need to find the text location
                        # within the document to provide proper text_segments
                    }
                }
                annotation['entities'].append(entity)
        
        return annotation
    
    def _save_training_dataset(self, training_samples: List[Dict], annotations: List[Dict]) -> Dict[str, str]:
        """Save training dataset to files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ensure dataset directory exists
        os.makedirs(self.dataset_path, exist_ok=True)
        
        # Save training samples
        dataset_filename = f"polish_invoice_training_dataset_{timestamp}.json"
        dataset_path = os.path.join(self.dataset_path, dataset_filename)
        
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'total_samples': len(training_samples),
                    'description': 'Polish Invoice OCR Training Dataset',
                    'version': '1.0'
                },
                'samples': training_samples
            }, f, ensure_ascii=False, indent=2)
        
        # Save Document AI annotations
        annotation_filename = f"document_ai_annotations_{timestamp}.jsonl"
        annotation_path = os.path.join(self.dataset_path, annotation_filename)
        
        with open(annotation_path, 'w', encoding='utf-8') as f:
            for annotation in annotations:
                f.write(json.dumps(annotation, ensure_ascii=False) + '\n')
        
        logger.info(f"Training dataset saved to: {dataset_path}")
        logger.info(f"Annotations saved to: {annotation_path}")
        
        return {
            'dataset_path': dataset_path,
            'annotation_path': annotation_path
        }
    
    def _calculate_dataset_statistics(self, training_samples: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for the training dataset"""
        
        if not training_samples:
            return {}
        
        # Confidence distribution
        confidences = [sample['confidence_score'] for sample in training_samples]
        
        # Validation score distribution
        validation_scores = [sample['validation_score'] for sample in training_samples]
        
        # Field coverage analysis
        field_coverage = {}
        total_samples = len(training_samples)
        
        for sample in training_samples:
            extracted_data = sample['extracted_data']
            for field, value in extracted_data.items():
                if value and value != 'None':  # Field has meaningful value
                    field_coverage[field] = field_coverage.get(field, 0) + 1
        
        # Convert to percentages
        for field in field_coverage:
            field_coverage[field] = (field_coverage[field] / total_samples) * 100
        
        # File type distribution
        file_types = {}
        for sample in training_samples:
            content_type = sample['metadata']['content_type']
            file_types[content_type] = file_types.get(content_type, 0) + 1
        
        statistics = {
            'total_samples': total_samples,
            'confidence_stats': {
                'min': min(confidences),
                'max': max(confidences),
                'avg': sum(confidences) / len(confidences)
            },
            'validation_stats': {
                'min': min(validation_scores),
                'max': max(validation_scores),
                'avg': sum(validation_scores) / len(validation_scores)
            },
            'field_coverage': field_coverage,
            'file_type_distribution': file_types,
            'recommendations': self._generate_training_recommendations(field_coverage, total_samples)
        }
        
        return statistics
    
    def _generate_training_recommendations(self, field_coverage: Dict[str, float], total_samples: int) -> List[str]:
        """Generate recommendations for improving training dataset"""
        
        recommendations = []
        
        # Check sample count
        if total_samples < 50:
            recommendations.append("Consider collecting more training samples (recommended: 100+ samples)")
        elif total_samples < 100:
            recommendations.append("Good sample count, but more data could improve accuracy")
        else:
            recommendations.append("Excellent sample count for training")
        
        # Check field coverage
        low_coverage_fields = [field for field, coverage in field_coverage.items() if coverage < 50]
        if low_coverage_fields:
            recommendations.append(f"Low coverage for fields: {', '.join(low_coverage_fields)}")
        
        # Check critical fields
        critical_fields = ['invoice_number', 'supplier_name', 'total_amount']
        missing_critical = [field for field in critical_fields if field_coverage.get(field, 0) < 80]
        if missing_critical:
            recommendations.append(f"Critical fields need more samples: {', '.join(missing_critical)}")
        
        return recommendations
    
    def _generate_document_ai_config(self, annotations: List[Dict]) -> Dict[str, Any]:
        """Generate configuration for Document AI custom training"""
        
        # Extract unique entity types from annotations
        entity_types = set()
        for annotation in annotations:
            for entity in annotation.get('entities', []):
                entity_types.add(entity['type'])
        
        config = {
            'training_config': {
                'dataset_type': 'INVOICE',
                'language_code': 'pl',  # Polish language
                'entity_types': list(entity_types),
                'training_samples_count': len(annotations),
                'recommended_training_time': '2-4 hours',
                'expected_accuracy_improvement': '5-15%'
            },
            'upload_instructions': [
                "1. Upload training documents to Google Cloud Storage bucket",
                "2. Create Document AI dataset with provided annotations",
                "3. Start custom training process",
                "4. Evaluate trained model performance",
                "5. Deploy improved model to production"
            ],
            'gcs_bucket': 'faktulove-ocr-training',
            'dataset_format': 'Document AI Custom Training Format'
        }
        
        return config
    
    def export_for_google_cloud(self, dataset_path: str) -> str:
        """
        Export training dataset in Google Cloud Document AI format
        
        Args:
            dataset_path: Path to the training dataset file
            
        Returns:
            Path to the exported GCS-ready dataset
        """
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            # Create GCS export format
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = dataset_path.replace('.json', f'_gcs_export_{timestamp}.json')
            
            gcs_format = {
                'dataset_name': f"polish_invoices_{timestamp}",
                'display_name': "Polish Invoice OCR Training Dataset",
                'description': "Custom training dataset for Polish invoice OCR accuracy improvement",
                'language_code': 'pl',
                'document_type': 'INVOICE',
                'training_documents': []
            }
            
            for sample in dataset['samples']:
                gcs_document = {
                    'document_url': f"gs://faktulove-ocr-training/{sample['original_filename']}",
                    'ground_truth': sample['ground_truth'],
                    'confidence_score': sample['confidence_score'],
                    'validation_score': sample['validation_score']
                }
                gcs_format['training_documents'].append(gcs_document)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(gcs_format, f, ensure_ascii=False, indent=2)
            
            logger.info(f"GCS export saved to: {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error exporting dataset for Google Cloud: {e}")
            raise
    
    def get_training_progress_report(self) -> Dict[str, Any]:
        """Get current training data collection progress"""
        
        total_ocr_results = OCRResult.objects.count()
        validated_results = OCRResult.objects.filter(ocrvalidation__isnull=False).count()
        high_quality_results = OCRResult.objects.filter(
            confidence_score__gte=self.min_confidence_threshold,
            ocrvalidation__accuracy_rating__gte=self.min_validation_score
        ).count()
        
        progress = {
            'total_processed_documents': total_ocr_results,
            'validated_documents': validated_results,
            'training_ready_documents': high_quality_results,
            'validation_rate': (validated_results / total_ocr_results * 100) if total_ocr_results > 0 else 0,
            'training_readiness': (high_quality_results / max(100, total_ocr_results) * 100),  # Target: 100 samples
            'recommendations': [
                f"Process more documents to reach 100+ training samples (current: {high_quality_results})",
                f"Validate more OCR results to improve training quality (current: {validated_results}/{total_ocr_results})",
                "Focus on validating high-confidence results for best training data quality"
            ]
        }
        
        return progress
