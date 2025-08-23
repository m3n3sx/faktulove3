"""
Django management command to collect OCR training data for custom model training
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from faktury.services.training_dataset_manager import TrainingDatasetManager
import json


class Command(BaseCommand):
    help = 'Collect high-quality OCR results for custom model training'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Maximum number of training samples to collect (default: 1000)'
        )
        
        parser.add_argument(
            '--export-gcs',
            action='store_true',
            help='Export dataset in Google Cloud Storage format'
        )
        
        parser.add_argument(
            '--min-confidence',
            type=float,
            default=95.0,
            help='Minimum confidence score for training data (default: 95.0)'
        )
        
        parser.add_argument(
            '--min-validation',
            type=int,
            default=8,
            help='Minimum validation score out of 10 (default: 8)'
        )
        
        parser.add_argument(
            '--output-dir',
            type=str,
            default='training_data/',
            help='Output directory for training dataset files'
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS('🚀 Starting OCR training data collection...')
            )
            
            # Initialize training dataset manager
            manager = TrainingDatasetManager()
            manager.min_confidence_threshold = options['min_confidence']
            manager.min_validation_score = options['min_validation']
            manager.dataset_path = options['output_dir']
            
            # Show current progress
            self.stdout.write('\n📊 Current Training Data Status:')
            progress = manager.get_training_progress_report()
            
            self.stdout.write(f"  Total processed documents: {progress['total_processed_documents']}")
            self.stdout.write(f"  Validated documents: {progress['validated_documents']}")
            self.stdout.write(f"  Training-ready documents: {progress['training_ready_documents']}")
            self.stdout.write(f"  Validation rate: {progress['validation_rate']:.1f}%")
            self.stdout.write(f"  Training readiness: {progress['training_readiness']:.1f}%")
            
            if progress['training_ready_documents'] < 10:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠️  Warning: Only {progress['training_ready_documents']} training-ready documents found."
                    )
                )
                self.stdout.write("   Recommendation: Process and validate more documents before training.")
                return
            
            # Collect training data
            self.stdout.write(f'\n🔍 Collecting training data (limit: {options["limit"]})...')
            
            result = manager.collect_training_data(limit=options['limit'])
            
            # Display results
            self.stdout.write('\n✅ Training data collection completed!')
            self.stdout.write(f"   Total samples collected: {result['total_samples']}")
            self.stdout.write(f"   Dataset saved to: {result['dataset_path']}")
            self.stdout.write(f"   Annotations saved to: {result['annotation_path']}")
            
            # Display statistics
            if 'statistics' in result:
                stats = result['statistics']
                self.stdout.write('\n📈 Dataset Statistics:')
                
                conf_stats = stats['confidence_stats']
                self.stdout.write(f"   Confidence range: {conf_stats['min']:.1f}% - {conf_stats['max']:.1f}%")
                self.stdout.write(f"   Average confidence: {conf_stats['avg']:.1f}%")
                
                val_stats = stats['validation_stats']
                self.stdout.write(f"   Validation score range: {val_stats['min']} - {val_stats['max']} (out of 10)")
                self.stdout.write(f"   Average validation: {val_stats['avg']:.1f}/10")
                
                # Field coverage
                self.stdout.write('\n📋 Field Coverage:')
                for field, coverage in sorted(stats['field_coverage'].items()):
                    if coverage >= 80:
                        style = self.style.SUCCESS
                        icon = '✅'
                    elif coverage >= 50:
                        style = self.style.WARNING  
                        icon = '⚠️'
                    else:
                        style = self.style.ERROR
                        icon = '❌'
                    
                    self.stdout.write(f"   {icon} {field}: {style(f'{coverage:.1f}%')}")
                
                # Recommendations
                if 'recommendations' in stats:
                    self.stdout.write('\n💡 Recommendations:')
                    for rec in stats['recommendations']:
                        self.stdout.write(f"   • {rec}")
            
            # Display Document AI configuration
            if 'document_ai_config' in result:
                config = result['document_ai_config']
                training_config = config['training_config']
                
                self.stdout.write('\n🤖 Document AI Training Configuration:')
                self.stdout.write(f"   Entity types: {len(training_config['entity_types'])} types")
                self.stdout.write(f"   Training samples: {training_config['training_samples_count']}")
                self.stdout.write(f"   Expected improvement: {training_config['expected_accuracy_improvement']}")
                self.stdout.write(f"   Recommended training time: {training_config['recommended_training_time']}")
            
            # Export for Google Cloud if requested
            if options['export_gcs']:
                self.stdout.write('\n☁️  Exporting for Google Cloud Storage...')
                try:
                    gcs_export_path = manager.export_for_google_cloud(result['dataset_path'])
                    self.stdout.write(f"   GCS export saved to: {gcs_export_path}")
                    
                    self.stdout.write('\n📦 Next Steps for Google Cloud Training:')
                    self.stdout.write('   1. Upload training documents to GCS bucket: faktulove-ocr-training')
                    self.stdout.write('   2. Create Document AI dataset using the exported annotations')
                    self.stdout.write('   3. Start custom training process in Google Cloud Console')
                    self.stdout.write('   4. Evaluate and deploy the trained model')
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"   Failed to export for GCS: {e}"))
            
            # Show file paths for reference
            self.stdout.write('\n📁 Generated Files:')
            self.stdout.write(f"   Training dataset: {result['dataset_path']}")
            self.stdout.write(f"   Document AI annotations: {result['annotation_path']}")
            if options['export_gcs']:
                self.stdout.write(f"   GCS export: {gcs_export_path}")
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Training data collection completed successfully!')
            )
            
        except Exception as e:
            raise CommandError(f'Training data collection failed: {e}')
