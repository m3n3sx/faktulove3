"""
Management command to set up intelligent caching strategies.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.apps import apps
import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up intelligent caching strategies for frequently accessed data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze-usage',
            action='store_true',
            help='Analyze data access patterns to identify caching opportunities'
        )
        parser.add_argument(
            '--setup-cache-keys',
            action='store_true',
            help='Set up cache key patterns and TTL strategies'
        )
        parser.add_argument(
            '--warm-cache',
            action='store_true',
            help='Pre-populate cache with frequently accessed data'
        )
        parser.add_argument(
            '--test-cache',
            action='store_true',
            help='Test cache performance and hit ratios'
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all cached data'
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Focus on specific model (e.g., faktury.Faktura)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up Intelligent Caching System')
        )
        
        try:
            if options['analyze_usage']:
                self.analyze_data_access_patterns(options.get('model'))
            
            if options['setup_cache_keys']:
                self.setup_cache_key_patterns()
            
            if options['warm_cache']:
                self.warm_cache_with_frequent_data(options.get('model'))
            
            if options['test_cache']:
                self.test_cache_performance()
            
            if options['clear_cache']:
                self.clear_all_cache()
            
            # If no specific option, run setup
            if not any([
                options['analyze_usage'],
                options['setup_cache_keys'],
                options['warm_cache'],
                options['test_cache'],
                options['clear_cache']
            ]):
                self.setup_complete_caching_system(options.get('model'))
            
            self.stdout.write(
                self.style.SUCCESS('✅ Intelligent caching setup completed')
            )
            
        except Exception as e:
            logger.error(f"Caching setup error: {e}")
            raise CommandError(f"Caching setup failed: {e}")
    
    def analyze_data_access_patterns(self, model_name: str = None):
        """Analyze data access patterns to identify caching opportunities"""
        self.stdout.write("📊 Analyzing data access patterns...")
        
        # Define models to analyze
        models_to_analyze = []
        
        if model_name:
            try:
                app_label, model_class = model_name.split('.')
                model = apps.get_model(app_label, model_class)
                models_to_analyze.append(model)
            except (ValueError, LookupError):
                self.stdout.write(f"❌ Invalid model: {model_name}")
                return
        else:
            # Analyze key models
            try:
                from faktury.models import Faktura, Kontrahent, Firma, OCRResult, DocumentUpload
                models_to_analyze = [Faktura, Kontrahent, Firma, OCRResult, DocumentUpload]
            except ImportError as e:
                self.stdout.write(f"⚠️ Could not import models: {e}")
                return
        
        caching_recommendations = {}
        
        for model in models_to_analyze:
            self.stdout.write(f"\n🔍 Analyzing {model.__name__}...")
            
            try:
                # Get basic statistics
                total_count = model.objects.count()
                
                # Analyze field access patterns
                field_analysis = self.analyze_model_fields(model)
                
                # Determine caching strategy
                strategy = self.determine_caching_strategy(model, total_count, field_analysis)
                
                caching_recommendations[model.__name__] = strategy
                
                self.stdout.write(f"  📈 Total records: {total_count}")
                self.stdout.write(f"  🎯 Recommended strategy: {strategy['strategy']}")
                self.stdout.write(f"  ⏱️ TTL: {strategy['ttl']} seconds")
                
                if strategy['cache_keys']:
                    self.stdout.write("  🔑 Recommended cache keys:")
                    for key in strategy['cache_keys']:
                        self.stdout.write(f"    - {key}")
                
            except Exception as e:
                self.stdout.write(f"  ❌ Error analyzing {model.__name__}: {e}")
        
        # Save recommendations
        cache.set('caching_recommendations', caching_recommendations, 3600)
        self.stdout.write(f"\n💾 Saved recommendations for {len(caching_recommendations)} models")
    
    def analyze_model_fields(self, model) -> Dict[str, Any]:
        """Analyze model fields to determine caching patterns"""
        field_analysis = {
            'foreign_keys': [],
            'indexed_fields': [],
            'unique_fields': [],
            'frequently_queried': []
        }
        
        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                field_analysis['foreign_keys'].append(field.name)
            
            if hasattr(field, 'db_index') and field.db_index:
                field_analysis['indexed_fields'].append(field.name)
            
            if hasattr(field, 'unique') and field.unique:
                field_analysis['unique_fields'].append(field.name)
        
        # Common frequently queried fields
        common_query_fields = ['id', 'pk', 'user', 'created_at', 'updated_at', 'status']
        for field_name in common_query_fields:
            if hasattr(model, field_name):
                field_analysis['frequently_queried'].append(field_name)
        
        return field_analysis
    
    def determine_caching_strategy(self, model, total_count: int, field_analysis: Dict) -> Dict[str, Any]:
        """Determine optimal caching strategy for a model"""
        model_name = model.__name__.lower()
        
        # Base strategy determination
        if total_count < 1000:
            strategy = 'full_cache'
            ttl = 3600  # 1 hour
        elif total_count < 10000:
            strategy = 'selective_cache'
            ttl = 1800  # 30 minutes
        else:
            strategy = 'query_cache'
            ttl = 900   # 15 minutes
        
        # Generate cache key patterns
        cache_keys = []
        
        # Individual object cache
        cache_keys.append(f"{model_name}_{{id}}")
        
        # User-specific caches
        if 'user' in field_analysis['foreign_keys']:
            cache_keys.append(f"{model_name}_user_{{user_id}}")
            cache_keys.append(f"{model_name}_user_{{user_id}}_list")
        
        # Status-based caches
        if hasattr(model, 'status'):
            cache_keys.append(f"{model_name}_status_{{status}}")
        
        # Foreign key caches
        for fk_field in field_analysis['foreign_keys']:
            cache_keys.append(f"{model_name}_{fk_field}_{{fk_id}}")
        
        # Unique field caches
        for unique_field in field_analysis['unique_fields']:
            cache_keys.append(f"{model_name}_{unique_field}_{{value}}")
        
        return {
            'strategy': strategy,
            'ttl': ttl,
            'cache_keys': cache_keys,
            'priority': self.get_model_priority(model_name),
            'invalidation_triggers': field_analysis['foreign_keys'] + ['updated_at']
        }
    
    def get_model_priority(self, model_name: str) -> str:
        """Get caching priority for model"""
        high_priority = ['faktura', 'kontrahent', 'firma']
        medium_priority = ['ocrresult', 'documentupload']
        
        if model_name in high_priority:
            return 'high'
        elif model_name in medium_priority:
            return 'medium'
        else:
            return 'low'
    
    def setup_cache_key_patterns(self):
        """Set up cache key patterns and TTL strategies"""
        self.stdout.write("🔑 Setting up cache key patterns...")
        
        cache_patterns = {
            # Static content caching
            'static_content': {
                'css_files': {'ttl': 86400, 'pattern': 'static_css_{version}'},
                'js_files': {'ttl': 86400, 'pattern': 'static_js_{version}'},
                'images': {'ttl': 86400, 'pattern': 'static_img_{hash}'},
            },
            
            # User data caching
            'user_data': {
                'profile': {'ttl': 3600, 'pattern': 'user_profile_{user_id}'},
                'preferences': {'ttl': 3600, 'pattern': 'user_prefs_{user_id}'},
                'permissions': {'ttl': 1800, 'pattern': 'user_perms_{user_id}'},
            },
            
            # Business data caching
            'business_data': {
                'invoices': {'ttl': 1800, 'pattern': 'invoices_user_{user_id}'},
                'companies': {'ttl': 3600, 'pattern': 'companies_user_{user_id}'},
                'contractors': {'ttl': 3600, 'pattern': 'contractors_user_{user_id}'},
            },
            
            # OCR data caching
            'ocr_data': {
                'results': {'ttl': 1800, 'pattern': 'ocr_result_{document_id}'},
                'processing_status': {'ttl': 300, 'pattern': 'ocr_status_{document_id}'},
                'confidence_scores': {'ttl': 1800, 'pattern': 'ocr_confidence_{document_id}'},
            },
            
            # API response caching
            'api_responses': {
                'list_endpoints': {'ttl': 300, 'pattern': 'api_list_{endpoint}_{user_id}_{page}'},
                'detail_endpoints': {'ttl': 600, 'pattern': 'api_detail_{endpoint}_{object_id}'},
                'search_results': {'ttl': 300, 'pattern': 'api_search_{query_hash}'},
            },
            
            # Performance data caching
            'performance_data': {
                'metrics': {'ttl': 300, 'pattern': 'perf_metrics_{timestamp}'},
                'reports': {'ttl': 1800, 'pattern': 'perf_report_{period}'},
                'system_health': {'ttl': 60, 'pattern': 'system_health'},
            }
        }
        
        # Store cache patterns configuration
        cache.set('cache_patterns_config', cache_patterns, 86400)  # 24 hours
        
        self.stdout.write("✅ Cache key patterns configured:")
        for category, patterns in cache_patterns.items():
            self.stdout.write(f"  📂 {category}: {len(patterns)} patterns")
    
    def warm_cache_with_frequent_data(self, model_name: str = None):
        """Pre-populate cache with frequently accessed data"""
        self.stdout.write("🔥 Warming cache with frequently accessed data...")
        
        try:
            # Get caching recommendations
            recommendations = cache.get('caching_recommendations', {})
            
            if not recommendations:
                self.stdout.write("⚠️ No caching recommendations found. Run --analyze-usage first.")
                return
            
            models_to_warm = []
            if model_name:
                if model_name in recommendations:
                    models_to_warm = [model_name]
                else:
                    self.stdout.write(f"❌ No recommendations for {model_name}")
                    return
            else:
                # Warm high-priority models
                models_to_warm = [
                    name for name, config in recommendations.items() 
                    if config.get('priority') == 'high'
                ]
            
            for model_name in models_to_warm:
                self.stdout.write(f"\n🔥 Warming cache for {model_name}...")
                self.warm_model_cache(model_name, recommendations[model_name])
            
        except Exception as e:
            self.stdout.write(f"❌ Error warming cache: {e}")
    
    def warm_model_cache(self, model_name: str, config: Dict[str, Any]):
        """Warm cache for a specific model"""
        try:
            # Get the model class
            app_label = 'faktury'  # Assuming all models are in faktury app
            model = apps.get_model(app_label, model_name)
            
            strategy = config['strategy']
            ttl = config['ttl']
            
            if strategy == 'full_cache':
                # Cache all objects
                objects = model.objects.all()[:1000]  # Limit to prevent memory issues
                for obj in objects:
                    cache_key = f"{model_name.lower()}_{obj.pk}"
                    cache.set(cache_key, obj, ttl)
                
                self.stdout.write(f"  ✅ Cached {len(objects)} {model_name} objects")
            
            elif strategy == 'selective_cache':
                # Cache recent/active objects
                if hasattr(model, 'created_at'):
                    recent_objects = model.objects.order_by('-created_at')[:100]
                elif hasattr(model, 'updated_at'):
                    recent_objects = model.objects.order_by('-updated_at')[:100]
                else:
                    recent_objects = model.objects.all()[:100]
                
                for obj in recent_objects:
                    cache_key = f"{model_name.lower()}_{obj.pk}"
                    cache.set(cache_key, obj, ttl)
                
                self.stdout.write(f"  ✅ Cached {len(recent_objects)} recent {model_name} objects")
            
            elif strategy == 'query_cache':
                # Cache common query results
                if hasattr(model, 'user'):
                    # Cache per-user queries
                    from django.contrib.auth.models import User
                    active_users = User.objects.filter(is_active=True)[:50]  # Top 50 active users
                    
                    for user in active_users:
                        user_objects = model.objects.filter(user=user)[:20]  # Top 20 per user
                        cache_key = f"{model_name.lower()}_user_{user.id}_list"
                        cache.set(cache_key, list(user_objects), ttl)
                    
                    self.stdout.write(f"  ✅ Cached user-specific {model_name} queries")
            
        except Exception as e:
            self.stdout.write(f"  ❌ Error warming {model_name} cache: {e}")
    
    def test_cache_performance(self):
        """Test cache performance and hit ratios"""
        self.stdout.write("🧪 Testing cache performance...")
        
        test_results = {}
        
        # Test basic cache operations
        self.stdout.write("  Testing basic operations...")
        
        # Test SET performance
        start_time = time.time()
        for i in range(100):
            cache.set(f"test_key_{i}", f"test_value_{i}", 300)
        set_time = time.time() - start_time
        test_results['set_operations'] = {'count': 100, 'time': set_time, 'avg': set_time/100}
        
        # Test GET performance
        start_time = time.time()
        hits = 0
        for i in range(100):
            value = cache.get(f"test_key_{i}")
            if value:
                hits += 1
        get_time = time.time() - start_time
        test_results['get_operations'] = {'count': 100, 'time': get_time, 'avg': get_time/100, 'hits': hits}
        
        # Test DELETE performance
        start_time = time.time()
        for i in range(100):
            cache.delete(f"test_key_{i}")
        delete_time = time.time() - start_time
        test_results['delete_operations'] = {'count': 100, 'time': delete_time, 'avg': delete_time/100}
        
        # Test large object caching
        large_data = {'data': 'x' * 10000}  # 10KB object
        start_time = time.time()
        cache.set('large_test_object', large_data, 300)
        large_set_time = time.time() - start_time
        
        start_time = time.time()
        retrieved_data = cache.get('large_test_object')
        large_get_time = time.time() - start_time
        
        test_results['large_objects'] = {
            'set_time': large_set_time,
            'get_time': large_get_time,
            'success': retrieved_data == large_data
        }
        
        # Clean up
        cache.delete('large_test_object')
        
        # Display results
        self.stdout.write("\n📊 Cache Performance Results:")
        self.stdout.write(f"  SET operations: {test_results['set_operations']['avg']*1000:.2f}ms avg")
        self.stdout.write(f"  GET operations: {test_results['get_operations']['avg']*1000:.2f}ms avg")
        self.stdout.write(f"  DELETE operations: {test_results['delete_operations']['avg']*1000:.2f}ms avg")
        self.stdout.write(f"  Hit ratio: {test_results['get_operations']['hits']}/100 ({test_results['get_operations']['hits']}%)")
        self.stdout.write(f"  Large object SET: {test_results['large_objects']['set_time']*1000:.2f}ms")
        self.stdout.write(f"  Large object GET: {test_results['large_objects']['get_time']*1000:.2f}ms")
        
        # Performance evaluation
        if test_results['get_operations']['avg'] < 0.001:  # < 1ms
            self.stdout.write("  ✅ Cache performance: Excellent")
        elif test_results['get_operations']['avg'] < 0.005:  # < 5ms
            self.stdout.write("  ✅ Cache performance: Good")
        else:
            self.stdout.write("  ⚠️ Cache performance: Needs optimization")
        
        # Store test results
        cache.set('cache_performance_test_results', test_results, 3600)
    
    def clear_all_cache(self):
        """Clear all cached data"""
        self.stdout.write("🧹 Clearing all cached data...")
        
        try:
            cache.clear()
            self.stdout.write("✅ All cache data cleared")
        except Exception as e:
            self.stdout.write(f"❌ Error clearing cache: {e}")
    
    def setup_complete_caching_system(self, model_name: str = None):
        """Set up complete intelligent caching system"""
        self.stdout.write("🚀 Setting up complete intelligent caching system...")
        
        # Run all setup steps
        self.analyze_data_access_patterns(model_name)
        self.setup_cache_key_patterns()
        self.warm_cache_with_frequent_data(model_name)
        self.test_cache_performance()
        
        # Generate final report
        self.generate_caching_report()
    
    def generate_caching_report(self):
        """Generate comprehensive caching report"""
        self.stdout.write("\n📋 Intelligent Caching System Report:")
        
        # Get stored data
        recommendations = cache.get('caching_recommendations', {})
        patterns = cache.get('cache_patterns_config', {})
        test_results = cache.get('cache_performance_test_results', {})
        
        self.stdout.write(f"  📊 Models analyzed: {len(recommendations)}")
        self.stdout.write(f"  🔑 Cache pattern categories: {len(patterns)}")
        
        if test_results:
            avg_get_time = test_results.get('get_operations', {}).get('avg', 0) * 1000
            hit_ratio = test_results.get('get_operations', {}).get('hits', 0)
            self.stdout.write(f"  ⚡ Average GET time: {avg_get_time:.2f}ms")
            self.stdout.write(f"  🎯 Cache hit ratio: {hit_ratio}%")
        
        self.stdout.write("\n💡 Caching Strategy Recommendations:")
        self.stdout.write("  1. Use cache warming for frequently accessed data")
        self.stdout.write("  2. Implement cache invalidation on data updates")
        self.stdout.write("  3. Monitor cache hit ratios and adjust TTL values")
        self.stdout.write("  4. Use cache tags for efficient bulk invalidation")
        self.stdout.write("  5. Consider Redis clustering for high-traffic scenarios")