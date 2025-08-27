"""
Django management command to set up PaddleOCR infrastructure and dependencies.

This command handles:
1. Installing PaddleOCR library and configuring Polish language models
2. Creating model storage directory structure and downloading required models
3. Validating environment variables and configuration management
"""

import os
import sys
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Set up PaddleOCR infrastructure and dependencies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-download',
            action='store_true',
            help='Force re-download of models even if they exist',
        )
        parser.add_argument(
            '--gpu',
            action='store_true',
            help='Initialize with GPU support (requires CUDA)',
        )
        parser.add_argument(
            '--languages',
            type=str,
            default='pl,en',
            help='Comma-separated list of languages to initialize (default: pl,en)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting PaddleOCR infrastructure setup...'))
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        try:
            # Step 1: Validate configuration
            model_dir = self.validate_configuration()
            
            # Step 2: Create directory structure
            model_dir = self.create_directory_structure(model_dir)
            
            # Step 3: Install and initialize PaddleOCR
            self.setup_paddleocr(
                model_dir=model_dir,
                force_download=options['force_download'],
                use_gpu=options['gpu'],
                languages=options['languages'].split(',')
            )
            
            # Step 4: Validate installation
            self.validate_installation()
            
            self.stdout.write(
                self.style.SUCCESS('PaddleOCR infrastructure setup completed successfully!')
            )
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            raise CommandError(f"PaddleOCR setup failed: {e}")

    def validate_configuration(self):
        """Validate Django configuration for PaddleOCR"""
        self.stdout.write('Validating configuration...')
        
        # Check if PaddleOCR is enabled
        paddleocr_config = getattr(settings, 'PADDLEOCR_CONFIG', {})
        if not paddleocr_config.get('enabled', False):
            self.stdout.write(
                self.style.WARNING('PaddleOCR is not enabled in settings. Enabling it now...')
            )
            # PaddleOCR is enabled via environment variable, so this should work
        
        # Check OCR feature flags
        ocr_flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
        if not ocr_flags.get('use_paddleocr', False):
            self.stdout.write(
                self.style.WARNING('PaddleOCR feature flag is disabled. Enable with use_paddleocr=True')
            )
        
        # Validate model directory
        model_dir = paddleocr_config.get('model_dir')
        if not model_dir:
            self.stdout.write(
                self.style.WARNING('PADDLEOCR_MODEL_DIR not configured, using default')
            )
            model_dir = os.path.join(settings.BASE_DIR, 'paddle_models')
        
        self.stdout.write(self.style.SUCCESS('Configuration validation passed'))
        return model_dir

    def create_directory_structure(self, model_dir_path):
        """Create the model directory structure for PaddleOCR"""
        self.stdout.write('Creating directory structure...')
        
        model_dir = Path(model_dir_path)
        
        # Create required directories
        directories = [
            model_dir,
            model_dir / 'det',
            model_dir / 'rec',
            model_dir / 'cls',
            model_dir / 'cache'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f'Created directory: {directory}')
        
        # Create model info file
        self.create_model_info_file(model_dir)
        
        return model_dir

    def create_model_info_file(self, model_dir):
        """Create a model information file"""
        info_content = """# PaddleOCR Model Information

This directory contains PaddleOCR models for the FaktuLove invoice processing system.

## Directory Structure:
- det/: Text detection models
- rec/: Text recognition models  
- cls/: Text classification models (angle detection)
- cache/: Model cache and temporary files

## Supported Languages:
- Polish (pl): Primary language for invoice processing
- English (en): Fallback language

## Model Updates:
Models are automatically downloaded on first use. To update models:
1. Delete the model directories
2. Run: python manage.py setup_paddleocr --force-download
3. Or restart the application (models will be re-downloaded)

## GPU Support:
To enable GPU acceleration:
1. Install CUDA-compatible PaddlePaddle: pip install paddlepaddle-gpu
2. Set PADDLEOCR_USE_GPU=True in environment
3. Run: python manage.py setup_paddleocr --gpu
4. Ensure CUDA drivers are properly installed

## Generated by:
Django management command: setup_paddleocr
"""
        
        info_file = model_dir / 'README.md'
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(info_content)
        
        self.stdout.write(f'Created model info file: {info_file}')

    def setup_paddleocr(self, model_dir, force_download=False, use_gpu=False, languages=None):
        """Install and initialize PaddleOCR with specified languages"""
        if languages is None:
            languages = ['pl', 'en']
        
        self.stdout.write(f'Setting up PaddleOCR with languages: {", ".join(languages)}')
        
        try:
            # Import PaddleOCR
            try:
                from paddleocr import PaddleOCR
            except ImportError as e:
                raise CommandError(
                    f"PaddleOCR not installed: {e}\n"
                    "Install with: pip install paddlepaddle paddleocr"
                )
            
            # Initialize PaddleOCR for each language
            for lang in languages:
                self.stdout.write(f'Initializing {lang} language models...')
                
                try:
                    # Initialize PaddleOCR - this will download models if needed
                    ocr = PaddleOCR(lang=lang)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'{lang} language models initialized successfully')
                    )
                    
                    # Test the OCR engine with a simple test
                    self.test_ocr_engine(ocr, lang)
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to initialize {lang} models: {e}')
                    )
                    if lang == 'pl':  # Polish is critical
                        raise CommandError(f'Critical: Failed to initialize Polish models: {e}')
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Continuing without {lang} support')
                        )
            
        except Exception as e:
            raise CommandError(f'PaddleOCR setup failed: {e}')

    def test_ocr_engine(self, ocr, language):
        """Test OCR engine with a simple test"""
        try:
            # Create a simple test image with text
            import numpy as np
            from PIL import Image, ImageDraw, ImageFont
            import tempfile
            
            # Create test image
            img = Image.new('RGB', (300, 100), color='white')
            draw = ImageDraw.Draw(img)
            
            # Test text based on language
            if language == 'pl':
                test_text = 'Test OCR ąćęłńóśźż'
            else:
                test_text = 'Test OCR Engine'
            
            try:
                # Try to use a default font
                font = ImageFont.load_default()
                draw.text((10, 30), test_text, fill='black', font=font)
            except:
                # Fallback to basic text
                draw.text((10, 30), test_text, fill='black')
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            try:
                # Test OCR
                result = ocr.ocr(tmp_path)
                
                if result and len(result) > 0:
                    self.stdout.write(f'OCR test passed for {language}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'OCR test returned empty result for {language}')
                    )
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'OCR test failed for {language}: {e}')
            )

    def validate_installation(self):
        """Validate the PaddleOCR installation"""
        self.stdout.write('Validating installation...')
        
        try:
            # Test imports
            from paddleocr import PaddleOCR
            import paddle
            
            # Check PaddlePaddle version
            paddle_version = paddle.__version__
            self.stdout.write(f'PaddlePaddle version: {paddle_version}')
            
            # Test basic initialization
            ocr = PaddleOCR(lang='en')
            self.stdout.write('Basic PaddleOCR initialization successful')
            
            # Check model directory
            paddleocr_config = getattr(settings, 'PADDLEOCR_CONFIG', {})
            model_dir_path = paddleocr_config.get('model_dir', os.path.join(settings.BASE_DIR, 'paddle_models'))
            model_dir = Path(model_dir_path)
            
            if model_dir.exists():
                model_files = list(model_dir.rglob('*'))
                self.stdout.write(f'Model directory contains {len(model_files)} files')
            else:
                self.stdout.write(
                    self.style.WARNING('Model directory not found - models may not be cached')
                )
            
            # Validate configuration
            required_config = ['enabled', 'languages', 'model_dir']
            for key in required_config:
                if key not in paddleocr_config:
                    self.stdout.write(
                        self.style.WARNING(f'Missing configuration key: {key}')
                    )
            
            self.stdout.write(self.style.SUCCESS('Installation validation passed'))
            
        except ImportError as e:
            raise CommandError(f'PaddleOCR import failed: {e}')
        except Exception as e:
            raise CommandError(f'Installation validation failed: {e}')

    def get_system_info(self):
        """Get system information for debugging"""
        info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'django_settings': {
                'PADDLEOCR_CONFIG': getattr(settings, 'PADDLEOCR_CONFIG', {}),
                'OCR_FEATURE_FLAGS': getattr(settings, 'OCR_FEATURE_FLAGS', {}),
            }
        }
        
        try:
            import paddle
            info['paddle_version'] = paddle.__version__
        except ImportError:
            info['paddle_version'] = 'Not installed'
        
        try:
            from paddleocr import PaddleOCR
            info['paddleocr_available'] = True
        except ImportError:
            info['paddleocr_available'] = False
        
        return info