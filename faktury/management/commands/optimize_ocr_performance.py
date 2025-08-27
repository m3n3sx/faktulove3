"""
Django management command to optimize OCR performance

This command runs comprehensive performance optimization for the OCR pipeline,
including profiling, parameter tuning, and cache optimization.
"""

import logging
import time
import os
from typing import List, Dict, Any
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from faktury.services.ocr_performance_profiler import ocr_profiler
from faktury.services.ocr_engine_optimizer import ocr_optimizer, OptimizationStrategy
from faktury.services.ocr_result_cache import ocr_cache
from faktury.services.parallel_ocr_processor import parallel_processor
from faktury.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize OCR performance through profiling and parameter tuning'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--strategy',
            type=str,
            choices=['speed_focused', 'accuracy_focused', 'balanced', 'polish_optimized'],
            default='balanced',
            help='Optimization strategy to use'
        )
        
        parser.add_argument(
            '--sample-documents',
            type=str,
            help='Directory containing sample documents for optimization'
        )
        
        parser.add_argument(
            '--max-optimization-time',
            type=int,
            default=300,
            help='Maximum time to spend on optimization (seconds)'
        )
        
        parser.add_argument(
            '--profile-only',
            action='store_true',
            help='Only run profiling without optimization'
        )
        
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear OCR result cache before optimization'
        )
        
        parser.add_argument(
            '--export-results',
            type=str,
            help='Export optimization results to file'
        )
        
        parser.add_argument(
            '--parallel-workers',
            type=int,
            default=4,
            help='Number of parallel workers for testing'
        )
    
    def handle(self, *args, **options):
        """Execute the optimization command"""
        try:
            self.stdout.write(
                self.style.SUCCESS('Starting OCR performance optimization...')
            )
            
            # Parse options
            strategy = OptimizationStrategy(options['strategy'])
            sample_dir = options.get('sample_documents')
            max_time = options['max_optimization_time']
            profile_only = options['profile_only']
            clear_cache = options['clear_cache']
            export_file = options.get('export_results')
            max_workers = options['parallel_workers']
            
            # Clear cache if requested
            if clear_cache:
                self.stdout.write('Clearing OCR result cache...')
                ocr_cache.clear_cache()
                ocr_profiler.clear_metrics()
            
            # Load sample documents
            sample_documents = self._load_sample_documents(sample_dir)
            if not sample_documents:
                raise CommandError('No sample documents found for optimization')
            
            self.stdout.write(f'Loaded {len(sample_documents)} sample documents')
            
            # Run profiling
            self.stdout.write('Running performance profiling...')
            profiling_results = self._run_profiling(sample_documents, max_workers)
            
            # Display profiling results
            self._display_profiling_results(profiling_results)
            
            if not profile_only:
                # Run optimization
                self.stdout.write(f'Running parameter optimization with strategy: {strategy.value}')
                optimization_results = self._run_optimization(
                    sample_documents, strategy, max_time
                )
                
                # Display optimization results
                self._display_optimization_results(optimization_results)
                
                # Test optimized parameters
                self.stdout.write('Testing optimized parameters...')
                test_results = self._test_optimized_parameters(
                    sample_documents, optimization_results, max_workers
                )
                
                # Display test results
                self._display_test_results(test_results)
            
            # Export results if requested
            if export_file:
                self._export_results(export_file, profiling_results, 
                                   optimization_results if not profile_only else None)
            
            # Display cache statistics
            self._display_cache_stats()
            
            self.stdout.write(
                self.style.SUCCESS('OCR performance optimization completed successfully!')
            )
            
        except Exception as e:
            logger.error(f"Optimization command failed: {e}", exc_info=True)
            raise CommandError(f'Optimization failed: {e}')
    
    def _load_sample_documents(self, sample_dir: str = None) -> List[bytes]:
        """Load sample documents for optimization"""
        sample_documents = []
        
        # Use provided directory or default
        if not sample_dir:
            sample_dir = os.path.join(settings.MEDIA_ROOT, 'ocr_uploads')
        
        if not os.path.exists(sample_dir):
            self.stdout.write(
                self.style.WARNING(f'Sample directory not found: {sample_dir}')
            )
            return []
        
        # Load sample files
        supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif']
        
        for root, dirs, files in os.walk(sample_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            if len(content) > 0:
                                sample_documents.append(content)
                                
                        # Limit to 10 samples for optimization
                        if len(sample_documents) >= 10:
                            break
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to load {file_path}: {e}')
                        )
            
            if len(sample_documents) >= 10:
                break
        
        return sample_documents
    
    def _run_profiling(self, sample_documents: List[bytes], max_workers: int) -> Dict[str, Any]:
        """Run performance profiling on sample documents"""
        processor = DocumentProcessor(
            max_workers=max_workers,
            enable_performance_optimization=True,
            enable_caching=False  # Disable caching for accurate profiling
        )
        
        if not processor.initialize():
            raise CommandError('Failed to initialize document processor')
        
        # Process sample documents with profiling
        results = []
        
        for i, document in enumerate(sample_documents):
            self.stdout.write(f'Profiling document {i+1}/{len(sample_documents)}...')
            
            try:
                # Determine MIME type (simplified)
                mime_type = 'application/pdf' if document[:4] == b'%PDF' else 'image/png'
                
                # Process with profiling
                with ocr_profiler.profile_stage(f"sample_document_{i}"):
                    result = processor.process_invoice(document, mime_type, f"sample_{i}")
                    results.append({
                        'document_index': i,
                        'success': result.success,
                        'confidence_score': result.confidence_score,
                        'processing_time': result.total_processing_time,
                        'engines_used': result.engines_used
                    })
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Profiling failed for document {i}: {e}')
                )
                results.append({
                    'document_index': i,
                    'success': False,
                    'error': str(e)
                })
        
        # Generate profiling report
        report = ocr_profiler.generate_report()
        
        return {
            'document_results': results,
            'profiler_report': report,
            'bottlenecks': report.bottlenecks,
            'recommendations': report.optimization_recommendations
        }
    
    def _run_optimization(self, sample_documents: List[bytes], 
                         strategy: OptimizationStrategy, max_time: int) -> Dict[str, Any]:
        """Run parameter optimization"""
        try:
            optimization_result = ocr_optimizer.optimize_parameters(
                document_samples=sample_documents,
                target_strategy=strategy,
                max_optimization_time=max_time
            )
            
            return {
                'optimized_parameters': optimization_result.optimized_parameters,
                'performance_improvement': optimization_result.performance_improvement,
                'optimization_time': optimization_result.optimization_time,
                'recommendations': optimization_result.recommendations
            }
            
        except Exception as e:
            raise CommandError(f'Parameter optimization failed: {e}')
    
    def _test_optimized_parameters(self, sample_documents: List[bytes],
                                 optimization_results: Dict[str, Any],
                                 max_workers: int) -> Dict[str, Any]:
        """Test optimized parameters on sample documents"""
        # Create processor with optimized parameters
        processor = DocumentProcessor(
            max_workers=max_workers,
            enable_performance_optimization=True,
            enable_caching=False
        )
        
        if not processor.initialize():
            raise CommandError('Failed to initialize optimized processor')
        
        # Test on sample documents
        test_results = []
        total_time = 0
        
        for i, document in enumerate(sample_documents[:5]):  # Test on first 5 documents
            try:
                mime_type = 'application/pdf' if document[:4] == b'%PDF' else 'image/png'
                
                start_time = time.time()
                result = processor.process_invoice(document, mime_type, f"test_{i}")
                processing_time = time.time() - start_time
                total_time += processing_time
                
                test_results.append({
                    'document_index': i,
                    'success': result.success,
                    'confidence_score': result.confidence_score,
                    'processing_time': processing_time,
                    'engines_used': result.engines_used
                })
                
            except Exception as e:
                test_results.append({
                    'document_index': i,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'test_results': test_results,
            'average_processing_time': total_time / len(test_results) if test_results else 0,
            'success_rate': sum(1 for r in test_results if r.get('success', False)) / len(test_results) if test_results else 0
        }
    
    def _display_profiling_results(self, results: Dict[str, Any]):
        """Display profiling results"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('PROFILING RESULTS'))
        self.stdout.write('='*60)
        
        # Document results summary
        doc_results = results['document_results']
        successful = sum(1 for r in doc_results if r.get('success', False))
        
        self.stdout.write(f'Documents processed: {len(doc_results)}')
        self.stdout.write(f'Successful: {successful}')
        self.stdout.write(f'Failed: {len(doc_results) - successful}')
        
        if successful > 0:
            avg_confidence = sum(r.get('confidence_score', 0) for r in doc_results if r.get('success', False)) / successful
            avg_time = sum(r.get('processing_time', 0) for r in doc_results if r.get('success', False)) / successful
            
            self.stdout.write(f'Average confidence: {avg_confidence:.1f}%')
            self.stdout.write(f'Average processing time: {avg_time:.2f}s')
        
        # Bottlenecks
        bottlenecks = results.get('bottlenecks', [])
        if bottlenecks:
            self.stdout.write('\nTop Bottlenecks:')
            for i, bottleneck in enumerate(bottlenecks[:3]):
                self.stdout.write(f'{i+1}. {bottleneck["stage_name"]} (score: {bottleneck["bottleneck_score"]})')
                for reason in bottleneck['reasons'][:2]:
                    self.stdout.write(f'   - {reason}')
        
        # Recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            self.stdout.write('\nOptimization Recommendations:')
            for i, rec in enumerate(recommendations[:5]):
                self.stdout.write(f'{i+1}. {rec}')
    
    def _display_optimization_results(self, results: Dict[str, Any]):
        """Display optimization results"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('OPTIMIZATION RESULTS'))
        self.stdout.write('='*60)
        
        improvement = results.get('performance_improvement', 0)
        opt_time = results.get('optimization_time', 0)
        
        self.stdout.write(f'Performance improvement: {improvement:.1f}%')
        self.stdout.write(f'Optimization time: {opt_time:.1f}s')
        
        # Optimized parameters summary
        params = results.get('optimized_parameters')
        if params:
            self.stdout.write(f'\nOptimized Parameters:')
            self.stdout.write(f'Strategy: {params.strategy.value}')
            self.stdout.write(f'Tesseract DPI: {params.tesseract_dpi}')
            self.stdout.write(f'EasyOCR Canvas Size: {params.easyocr_canvas_size}')
            self.stdout.write(f'Max Processing Time: {params.max_processing_time}s')
            self.stdout.write(f'Min Confidence Threshold: {params.min_confidence_threshold}%')
        
        # Recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            self.stdout.write('\nOptimization Recommendations:')
            for i, rec in enumerate(recommendations[:5]):
                self.stdout.write(f'{i+1}. {rec}')
    
    def _display_test_results(self, results: Dict[str, Any]):
        """Display test results"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('OPTIMIZED PARAMETERS TEST RESULTS'))
        self.stdout.write('='*60)
        
        avg_time = results.get('average_processing_time', 0)
        success_rate = results.get('success_rate', 0)
        
        self.stdout.write(f'Average processing time: {avg_time:.2f}s')
        self.stdout.write(f'Success rate: {success_rate:.1%}')
        
        test_results = results.get('test_results', [])
        if test_results:
            successful_results = [r for r in test_results if r.get('success', False)]
            if successful_results:
                avg_confidence = sum(r.get('confidence_score', 0) for r in successful_results) / len(successful_results)
                self.stdout.write(f'Average confidence: {avg_confidence:.1f}%')
    
    def _display_cache_stats(self):
        """Display cache statistics"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('CACHE STATISTICS'))
        self.stdout.write('='*60)
        
        stats = ocr_cache.get_stats()
        
        self.stdout.write(f'Total entries: {stats.total_entries}')
        self.stdout.write(f'Cache size: {stats.total_size_mb:.1f}MB')
        self.stdout.write(f'Hit rate: {stats.hit_rate:.1%}')
        self.stdout.write(f'Space saved: {stats.space_saved_hours:.1f} hours')
        
        if stats.most_cached_types:
            self.stdout.write('\nMost cached document types:')
            for mime_type, count in stats.most_cached_types:
                self.stdout.write(f'  {mime_type}: {count} entries')
    
    def _export_results(self, export_file: str, profiling_results: Dict[str, Any],
                       optimization_results: Dict[str, Any] = None):
        """Export results to file"""
        try:
            export_data = {
                'export_timestamp': time.time(),
                'profiling_results': profiling_results,
                'optimization_results': optimization_results,
                'cache_stats': ocr_cache.get_stats().__dict__
            }
            
            # Export profiler metrics
            ocr_profiler.export_metrics(f"{export_file}_profiler.json")
            
            # Export optimizer results
            if optimization_results:
                ocr_optimizer.save_optimization_results(f"{export_file}_optimizer.json")
            
            self.stdout.write(f'Results exported to {export_file}_*.json')
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to export results: {e}')
            )