"""
OCR Result Caching System

This module provides intelligent caching for OCR results based on document
similarity, content hashing, and processing patterns to improve performance
for frequently processed document types.
"""

import logging
import hashlib
import pickle
import json
import time
import os
import threading
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import sqlite3
from datetime import datetime, timedelta
import numpy as np
from difflib import SequenceMatcher

from .ocr_performance_profiler import ocr_profiler

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """OCR result cache entry"""
    content_hash: str
    similarity_hash: str
    ocr_result: Dict[str, Any]
    confidence_score: float
    processing_time: float
    engines_used: List[str]
    created_timestamp: float
    last_accessed: float
    access_count: int = 0
    file_size: int = 0
    mime_type: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStats:
    """Cache statistics"""
    total_entries: int = 0
    total_size_mb: float = 0.0
    hit_count: int = 0
    miss_count: int = 0
    hit_rate: float = 0.0
    average_confidence: float = 0.0
    space_saved_hours: float = 0.0
    most_cached_types: List[Tuple[str, int]] = field(default_factory=list)


class DocumentSimilarityAnalyzer:
    """Analyze document similarity for intelligent caching"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize similarity analyzer
        
        Args:
            similarity_threshold: Minimum similarity for cache hits
        """
        self.similarity_threshold = similarity_threshold
        self.feature_extractors = {
            'text_length': self._extract_text_length_features,
            'layout_structure': self._extract_layout_features,
            'content_patterns': self._extract_content_patterns,
            'visual_features': self._extract_visual_features
        }
    
    def calculate_similarity(self, doc1_features: Dict[str, Any], 
                           doc2_features: Dict[str, Any]) -> float:
        """Calculate similarity score between two documents"""
        try:
            similarity_scores = []
            
            # Text length similarity
            len1 = doc1_features.get('text_length', 0)
            len2 = doc2_features.get('text_length', 0)
            if len1 > 0 and len2 > 0:
                length_sim = 1.0 - abs(len1 - len2) / max(len1, len2)
                similarity_scores.append(length_sim * 0.2)  # 20% weight
            
            # Layout structure similarity
            layout1 = doc1_features.get('layout_structure', {})
            layout2 = doc2_features.get('layout_structure', {})
            layout_sim = self._compare_layouts(layout1, layout2)
            similarity_scores.append(layout_sim * 0.3)  # 30% weight
            
            # Content pattern similarity
            patterns1 = doc1_features.get('content_patterns', set())
            patterns2 = doc2_features.get('content_patterns', set())
            if patterns1 and patterns2:
                pattern_sim = len(patterns1.intersection(patterns2)) / len(patterns1.union(patterns2))
                similarity_scores.append(pattern_sim * 0.3)  # 30% weight
            
            # Visual feature similarity
            visual1 = doc1_features.get('visual_features', {})
            visual2 = doc2_features.get('visual_features', {})
            visual_sim = self._compare_visual_features(visual1, visual2)
            similarity_scores.append(visual_sim * 0.2)  # 20% weight
            
            return sum(similarity_scores) if similarity_scores else 0.0
            
        except Exception as e:
            logger.warning(f"Similarity calculation failed: {e}")
            return 0.0
    
    def extract_features(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Extract features from document for similarity analysis"""
        features = {
            'mime_type': mime_type,
            'file_size': len(file_content),
            'extraction_timestamp': time.time()
        }
        
        try:
            # Extract different types of features
            for feature_type, extractor in self.feature_extractors.items():
                try:
                    features[feature_type] = extractor(file_content, mime_type)
                except Exception as e:
                    logger.warning(f"Feature extraction failed for {feature_type}: {e}")
                    features[feature_type] = {}
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return features
    
    def _extract_text_length_features(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Extract text length-based features"""
        # Simplified - in practice, you'd do basic OCR or text extraction
        return {
            'estimated_text_length': len(file_content) // 100,  # Rough estimate
            'file_size': len(file_content)
        }
    
    def _extract_layout_features(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Extract layout structure features"""
        try:
            if mime_type == 'application/pdf':
                # For PDFs, analyze page structure
                return {
                    'page_count': 1,  # Simplified
                    'estimated_blocks': len(file_content) // 1000,
                    'document_type': 'pdf'
                }
            else:
                # For images, analyze dimensions and structure
                from PIL import Image
                import io
                
                image = Image.open(io.BytesIO(file_content))
                width, height = image.size
                
                return {
                    'width': width,
                    'height': height,
                    'aspect_ratio': width / height if height > 0 else 1.0,
                    'estimated_text_blocks': (width * height) // 50000,
                    'document_type': 'image'
                }
        except Exception as e:
            logger.warning(f"Layout feature extraction failed: {e}")
            return {}
    
    def _extract_content_patterns(self, file_content: bytes, mime_type: str) -> Set[str]:
        """Extract content patterns for similarity matching"""
        patterns = set()
        
        try:
            # Convert to string for pattern analysis (simplified)
            content_str = str(file_content[:1000])  # First 1KB for patterns
            
            # Look for common invoice patterns
            if 'faktura' in content_str.lower():
                patterns.add('polish_invoice')
            if 'vat' in content_str.lower():
                patterns.add('vat_document')
            if any(char in content_str for char in 'ąćęłńóśźż'):
                patterns.add('polish_text')
            if any(pattern in content_str for pattern in ['€', '$', 'zł', 'PLN']):
                patterns.add('currency_document')
            
            # Add MIME type pattern
            patterns.add(f"type_{mime_type.replace('/', '_')}")
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Content pattern extraction failed: {e}")
            return patterns
    
    def _extract_visual_features(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Extract visual features from document"""
        try:
            if mime_type.startswith('image/'):
                from PIL import Image
                import io
                
                image = Image.open(io.BytesIO(file_content))
                
                # Convert to grayscale for analysis
                gray_image = image.convert('L')
                pixels = list(gray_image.getdata())
                
                return {
                    'brightness_avg': sum(pixels) / len(pixels),
                    'brightness_std': np.std(pixels),
                    'dark_pixel_ratio': sum(1 for p in pixels if p < 128) / len(pixels),
                    'image_mode': image.mode,
                    'has_transparency': image.mode in ('RGBA', 'LA')
                }
            else:
                return {'document_type': 'non_image'}
                
        except Exception as e:
            logger.warning(f"Visual feature extraction failed: {e}")
            return {}
    
    def _compare_layouts(self, layout1: Dict[str, Any], layout2: Dict[str, Any]) -> float:
        """Compare layout structures"""
        if not layout1 or not layout2:
            return 0.0
        
        similarity_factors = []
        
        # Compare aspect ratios
        if 'aspect_ratio' in layout1 and 'aspect_ratio' in layout2:
            ratio_diff = abs(layout1['aspect_ratio'] - layout2['aspect_ratio'])
            ratio_sim = max(0, 1.0 - ratio_diff)
            similarity_factors.append(ratio_sim)
        
        # Compare estimated text blocks
        if 'estimated_text_blocks' in layout1 and 'estimated_text_blocks' in layout2:
            blocks1 = layout1['estimated_text_blocks']
            blocks2 = layout2['estimated_text_blocks']
            if blocks1 > 0 and blocks2 > 0:
                block_sim = 1.0 - abs(blocks1 - blocks2) / max(blocks1, blocks2)
                similarity_factors.append(block_sim)
        
        return sum(similarity_factors) / len(similarity_factors) if similarity_factors else 0.0
    
    def _compare_visual_features(self, visual1: Dict[str, Any], visual2: Dict[str, Any]) -> float:
        """Compare visual features"""
        if not visual1 or not visual2:
            return 0.0
        
        similarity_factors = []
        
        # Compare brightness
        if 'brightness_avg' in visual1 and 'brightness_avg' in visual2:
            brightness_diff = abs(visual1['brightness_avg'] - visual2['brightness_avg'])
            brightness_sim = max(0, 1.0 - brightness_diff / 255.0)
            similarity_factors.append(brightness_sim)
        
        # Compare dark pixel ratio
        if 'dark_pixel_ratio' in visual1 and 'dark_pixel_ratio' in visual2:
            ratio_diff = abs(visual1['dark_pixel_ratio'] - visual2['dark_pixel_ratio'])
            ratio_sim = max(0, 1.0 - ratio_diff)
            similarity_factors.append(ratio_sim)
        
        return sum(similarity_factors) / len(similarity_factors) if similarity_factors else 0.0


class OCRResultCache:
    """
    Intelligent OCR result caching system
    
    Features:
    - Content-based and similarity-based caching
    - Automatic cache eviction and cleanup
    - Performance analytics and optimization
    - Persistent storage with SQLite
    - Thread-safe operations
    """
    
    def __init__(self,
                 cache_dir: str = None,
                 max_cache_size_mb: float = 1024.0,
                 max_entries: int = 10000,
                 similarity_threshold: float = 0.85,
                 enable_similarity_matching: bool = True,
                 cleanup_interval_hours: float = 24.0):
        """
        Initialize OCR result cache
        
        Args:
            cache_dir: Directory for cache storage
            max_cache_size_mb: Maximum cache size in MB
            max_entries: Maximum number of cache entries
            similarity_threshold: Similarity threshold for cache hits
            enable_similarity_matching: Enable similarity-based matching
            cleanup_interval_hours: Automatic cleanup interval
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), '.ocr_result_cache')
        self.max_cache_size_mb = max_cache_size_mb
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        self.enable_similarity_matching = enable_similarity_matching
        self.cleanup_interval_hours = cleanup_interval_hours
        
        # Initialize components
        self.similarity_analyzer = DocumentSimilarityAnalyzer(similarity_threshold)
        
        # Cache storage
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.similarity_index: Dict[str, List[str]] = defaultdict(list)  # similarity_hash -> content_hashes
        self.feature_cache: Dict[str, Dict[str, Any]] = {}  # content_hash -> features
        
        # Statistics
        self.stats = CacheStats()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Database connection
        self.db_path = os.path.join(self.cache_dir, 'ocr_cache.db')
        self.db_connection: Optional[sqlite3.Connection] = None
        
        # Cleanup thread
        self.cleanup_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        
        # Initialize cache
        self._initialize_cache()
        
        logger.info(f"OCR Result Cache initialized with {max_entries} max entries, "
                   f"{max_cache_size_mb}MB max size")
    
    def _initialize_cache(self):
        """Initialize cache storage and database"""
        try:
            # Create cache directory
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # Initialize database
            self._initialize_database()
            
            # Load existing cache entries
            self._load_cache_from_database()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            self.cleanup_thread.start()
            
            logger.info("OCR cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OCR cache: {e}")
            raise
    
    def _initialize_database(self):
        """Initialize SQLite database for persistent storage"""
        try:
            self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.db_connection.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    content_hash TEXT PRIMARY KEY,
                    similarity_hash TEXT,
                    ocr_result TEXT,
                    confidence_score REAL,
                    processing_time REAL,
                    engines_used TEXT,
                    created_timestamp REAL,
                    last_accessed REAL,
                    access_count INTEGER,
                    file_size INTEGER,
                    mime_type TEXT,
                    metadata TEXT
                )
            ''')
            
            self.db_connection.execute('''
                CREATE INDEX IF NOT EXISTS idx_similarity_hash ON cache_entries(similarity_hash)
            ''')
            
            self.db_connection.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            ''')
            
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _load_cache_from_database(self):
        """Load cache entries from database into memory"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT * FROM cache_entries 
                ORDER BY last_accessed DESC 
                LIMIT ?
            ''', (self.max_entries // 2,))  # Load half of max entries
            
            for row in cursor.fetchall():
                entry = CacheEntry(
                    content_hash=row[0],
                    similarity_hash=row[1],
                    ocr_result=json.loads(row[2]),
                    confidence_score=row[3],
                    processing_time=row[4],
                    engines_used=json.loads(row[5]),
                    created_timestamp=row[6],
                    last_accessed=row[7],
                    access_count=row[8],
                    file_size=row[9],
                    mime_type=row[10],
                    metadata=json.loads(row[11]) if row[11] else {}
                )
                
                self.memory_cache[entry.content_hash] = entry
                self.similarity_index[entry.similarity_hash].append(entry.content_hash)
            
            self._update_stats()
            logger.info(f"Loaded {len(self.memory_cache)} cache entries from database")
            
        except Exception as e:
            logger.error(f"Failed to load cache from database: {e}")
    
    @ocr_profiler.profile_function("cache_lookup")
    def get(self, file_content: bytes, mime_type: str) -> Optional[Dict[str, Any]]:
        """
        Get OCR result from cache
        
        Args:
            file_content: Document content
            mime_type: MIME type of document
            
        Returns:
            Cached OCR result or None if not found
        """
        try:
            with self._lock:
                # Generate content hash
                content_hash = self._generate_content_hash(file_content)
                
                # Check exact match first
                if content_hash in self.memory_cache:
                    entry = self.memory_cache[content_hash]
                    entry.last_accessed = time.time()
                    entry.access_count += 1
                    
                    # Move to end (most recently used)
                    self.memory_cache.move_to_end(content_hash)
                    
                    self.stats.hit_count += 1
                    self._update_hit_rate()
                    
                    logger.debug(f"Cache hit (exact) for content hash: {content_hash[:8]}...")
                    return entry.ocr_result
                
                # Try similarity matching if enabled
                if self.enable_similarity_matching:
                    similar_result = self._find_similar_result(file_content, mime_type, content_hash)
                    if similar_result:
                        self.stats.hit_count += 1
                        self._update_hit_rate()
                        logger.debug(f"Cache hit (similar) for content hash: {content_hash[:8]}...")
                        return similar_result
                
                # Cache miss
                self.stats.miss_count += 1
                self._update_hit_rate()
                return None
                
        except Exception as e:
            logger.error(f"Cache lookup failed: {e}")
            self.stats.miss_count += 1
            self._update_hit_rate()
            return None
    
    @ocr_profiler.profile_function("cache_storage")
    def put(self, file_content: bytes, mime_type: str, ocr_result: Dict[str, Any]):
        """
        Store OCR result in cache
        
        Args:
            file_content: Document content
            mime_type: MIME type of document
            ocr_result: OCR processing result
        """
        try:
            with self._lock:
                # Generate hashes
                content_hash = self._generate_content_hash(file_content)
                
                # Extract features for similarity matching
                features = None
                similarity_hash = ""
                if self.enable_similarity_matching:
                    features = self.similarity_analyzer.extract_features(file_content, mime_type)
                    similarity_hash = self._generate_similarity_hash(features)
                    self.feature_cache[content_hash] = features
                
                # Create cache entry
                entry = CacheEntry(
                    content_hash=content_hash,
                    similarity_hash=similarity_hash,
                    ocr_result=ocr_result,
                    confidence_score=ocr_result.get('confidence_score', 0.0),
                    processing_time=ocr_result.get('processing_time', 0.0),
                    engines_used=ocr_result.get('engines_used', []),
                    created_timestamp=time.time(),
                    last_accessed=time.time(),
                    access_count=1,
                    file_size=len(file_content),
                    mime_type=mime_type
                )
                
                # Check cache limits before adding
                if len(self.memory_cache) >= self.max_entries:
                    self._evict_entries()
                
                # Add to memory cache
                self.memory_cache[content_hash] = entry
                
                # Add to similarity index
                if similarity_hash:
                    self.similarity_index[similarity_hash].append(content_hash)
                
                # Persist to database
                self._persist_entry(entry)
                
                self._update_stats()
                
                logger.debug(f"Cached OCR result for content hash: {content_hash[:8]}...")
                
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    def _find_similar_result(self, file_content: bytes, mime_type: str, 
                           content_hash: str) -> Optional[Dict[str, Any]]:
        """Find similar cached result using similarity matching"""
        try:
            # Extract features for the new document
            features = self.similarity_analyzer.extract_features(file_content, mime_type)
            similarity_hash = self._generate_similarity_hash(features)
            
            # Look for entries with the same similarity hash
            candidate_hashes = self.similarity_index.get(similarity_hash, [])
            
            best_similarity = 0.0
            best_entry = None
            
            for candidate_hash in candidate_hashes:
                if candidate_hash == content_hash:
                    continue
                
                if candidate_hash not in self.memory_cache:
                    continue
                
                # Get cached features
                cached_features = self.feature_cache.get(candidate_hash)
                if not cached_features:
                    continue
                
                # Calculate similarity
                similarity = self.similarity_analyzer.calculate_similarity(features, cached_features)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_entry = self.memory_cache[candidate_hash]
            
            if best_entry:
                # Update access statistics
                best_entry.last_accessed = time.time()
                best_entry.access_count += 1
                
                # Move to end (most recently used)
                self.memory_cache.move_to_end(best_entry.content_hash)
                
                # Add similarity metadata to result
                result = best_entry.ocr_result.copy()
                result['cache_similarity_score'] = best_similarity
                result['cache_match_type'] = 'similar'
                
                return result
            
            return None
            
        except Exception as e:
            logger.warning(f"Similarity matching failed: {e}")
            return None
    
    def _generate_content_hash(self, file_content: bytes) -> str:
        """Generate content hash for exact matching"""
        return hashlib.sha256(file_content).hexdigest()
    
    def _generate_similarity_hash(self, features: Dict[str, Any]) -> str:
        """Generate similarity hash for approximate matching"""
        try:
            # Create a simplified hash based on key features
            hash_components = []
            
            # MIME type
            hash_components.append(features.get('mime_type', ''))
            
            # File size bucket (group similar sizes)
            file_size = features.get('file_size', 0)
            size_bucket = (file_size // 10000) * 10000  # 10KB buckets
            hash_components.append(str(size_bucket))
            
            # Layout features
            layout = features.get('layout_structure', {})
            if 'aspect_ratio' in layout:
                # Round aspect ratio to 1 decimal place
                aspect_bucket = round(layout['aspect_ratio'], 1)
                hash_components.append(str(aspect_bucket))
            
            # Content patterns
            patterns = features.get('content_patterns', set())
            sorted_patterns = sorted(list(patterns))
            hash_components.extend(sorted_patterns)
            
            # Create hash
            hash_string = '|'.join(hash_components)
            return hashlib.md5(hash_string.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Similarity hash generation failed: {e}")
            return hashlib.md5(str(features).encode()).hexdigest()
    
    def _evict_entries(self):
        """Evict least recently used entries"""
        try:
            # Calculate how many entries to evict (25% of max)
            evict_count = max(1, self.max_entries // 4)
            
            # Get LRU entries
            lru_entries = list(self.memory_cache.items())[:evict_count]
            
            for content_hash, entry in lru_entries:
                # Remove from memory cache
                del self.memory_cache[content_hash]
                
                # Remove from similarity index
                if entry.similarity_hash in self.similarity_index:
                    if content_hash in self.similarity_index[entry.similarity_hash]:
                        self.similarity_index[entry.similarity_hash].remove(content_hash)
                    
                    # Clean up empty similarity hash entries
                    if not self.similarity_index[entry.similarity_hash]:
                        del self.similarity_index[entry.similarity_hash]
                
                # Remove from feature cache
                if content_hash in self.feature_cache:
                    del self.feature_cache[content_hash]
            
            logger.debug(f"Evicted {evict_count} cache entries")
            
        except Exception as e:
            logger.error(f"Cache eviction failed: {e}")
    
    def _persist_entry(self, entry: CacheEntry):
        """Persist cache entry to database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cache_entries 
                (content_hash, similarity_hash, ocr_result, confidence_score, processing_time,
                 engines_used, created_timestamp, last_accessed, access_count, file_size,
                 mime_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.content_hash,
                entry.similarity_hash,
                json.dumps(entry.ocr_result),
                entry.confidence_score,
                entry.processing_time,
                json.dumps(entry.engines_used),
                entry.created_timestamp,
                entry.last_accessed,
                entry.access_count,
                entry.file_size,
                entry.mime_type,
                json.dumps(entry.metadata)
            ))
            
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to persist cache entry: {e}")
    
    def _update_stats(self):
        """Update cache statistics"""
        try:
            self.stats.total_entries = len(self.memory_cache)
            
            # Calculate total size
            total_size = 0
            confidence_scores = []
            processing_times = []
            mime_type_counts = defaultdict(int)
            
            for entry in self.memory_cache.values():
                # Estimate entry size
                entry_size = (
                    len(json.dumps(entry.ocr_result)) +
                    len(entry.content_hash) +
                    len(entry.similarity_hash) +
                    entry.file_size // 10  # Rough estimate
                )
                total_size += entry_size
                
                confidence_scores.append(entry.confidence_score)
                processing_times.append(entry.processing_time)
                mime_type_counts[entry.mime_type] += 1
            
            self.stats.total_size_mb = total_size / 1024 / 1024
            
            if confidence_scores:
                self.stats.average_confidence = sum(confidence_scores) / len(confidence_scores)
            
            if processing_times:
                self.stats.space_saved_hours = sum(processing_times) / 3600
            
            # Most cached types
            self.stats.most_cached_types = sorted(
                mime_type_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
        except Exception as e:
            logger.warning(f"Stats update failed: {e}")
    
    def _update_hit_rate(self):
        """Update cache hit rate"""
        total_requests = self.stats.hit_count + self.stats.miss_count
        if total_requests > 0:
            self.stats.hit_rate = self.stats.hit_count / total_requests
    
    def _cleanup_worker(self):
        """Background cleanup worker"""
        logger.debug("Cache cleanup worker started")
        
        while not self.shutdown_event.is_set():
            try:
                # Wait for cleanup interval
                if self.shutdown_event.wait(self.cleanup_interval_hours * 3600):
                    break
                
                # Perform cleanup
                self._cleanup_expired_entries()
                self._optimize_database()
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
        
        logger.debug("Cache cleanup worker stopped")
    
    def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        try:
            current_time = time.time()
            expiry_time = current_time - (30 * 24 * 3600)  # 30 days
            
            with self._lock:
                # Remove expired entries from memory
                expired_hashes = [
                    content_hash for content_hash, entry in self.memory_cache.items()
                    if entry.last_accessed < expiry_time
                ]
                
                for content_hash in expired_hashes:
                    entry = self.memory_cache[content_hash]
                    del self.memory_cache[content_hash]
                    
                    # Clean up similarity index
                    if entry.similarity_hash in self.similarity_index:
                        if content_hash in self.similarity_index[entry.similarity_hash]:
                            self.similarity_index[entry.similarity_hash].remove(content_hash)
                        
                        if not self.similarity_index[entry.similarity_hash]:
                            del self.similarity_index[entry.similarity_hash]
                    
                    # Clean up feature cache
                    if content_hash in self.feature_cache:
                        del self.feature_cache[content_hash]
                
                # Remove expired entries from database
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM cache_entries WHERE last_accessed < ?', (expiry_time,))
                deleted_count = cursor.rowcount
                self.db_connection.commit()
                
                if expired_hashes or deleted_count > 0:
                    logger.info(f"Cleaned up {len(expired_hashes)} memory entries and "
                               f"{deleted_count} database entries")
                
                self._update_stats()
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def _optimize_database(self):
        """Optimize database performance"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('VACUUM')
            cursor.execute('ANALYZE')
            self.db_connection.commit()
            logger.debug("Database optimized")
            
        except Exception as e:
            logger.warning(f"Database optimization failed: {e}")
    
    def get_stats(self) -> CacheStats:
        """Get current cache statistics"""
        with self._lock:
            self._update_stats()
            return self.stats
    
    def clear_cache(self):
        """Clear all cache entries"""
        try:
            with self._lock:
                self.memory_cache.clear()
                self.similarity_index.clear()
                self.feature_cache.clear()
                
                # Clear database
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM cache_entries')
                self.db_connection.commit()
                
                # Reset statistics
                self.stats = CacheStats()
                
                logger.info("Cache cleared")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def shutdown(self):
        """Shutdown cache system"""
        try:
            logger.info("Shutting down OCR cache")
            
            # Signal shutdown
            self.shutdown_event.set()
            
            # Wait for cleanup thread
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5.0)
            
            # Close database connection
            if self.db_connection:
                self.db_connection.close()
            
            logger.info("OCR cache shutdown complete")
            
        except Exception as e:
            logger.error(f"Cache shutdown error: {e}")


# Global cache instance
ocr_cache = OCRResultCache()