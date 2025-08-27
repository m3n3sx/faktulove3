#!/usr/bin/env python3
"""
Asset minification script for FaktuLove
Minifies CSS and JavaScript files to reduce file sizes and improve loading performance.
"""

import os
import re
import gzip
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssetMinifier:
    """Minifies CSS and JavaScript files"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = Path(static_dir)
        self.backup_dir = self.static_dir / "backup"
        self.minified_dir = self.static_dir / "minified"
        
        # Create directories
        self.backup_dir.mkdir(exist_ok=True)
        self.minified_dir.mkdir(exist_ok=True)
    
    def minify_css(self, css_content: str) -> str:
        """Minify CSS content by removing unnecessary whitespace and comments"""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r'}\s*', '}', css_content)
        css_content = re.sub(r':\s*', ':', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        css_content = re.sub(r',\s*', ',', css_content)
        
        # Remove leading/trailing whitespace
        css_content = css_content.strip()
        
        return css_content
    
    def minify_js(self, js_content: str) -> str:
        """Minify JavaScript content by removing comments and unnecessary whitespace"""
        # Remove single-line comments (but not URLs)
        js_content = re.sub(r'(?<!:)\/\/.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        js_content = re.sub(r';\s*}', '}', js_content)
        js_content = re.sub(r'{\s*', '{', js_content)
        js_content = re.sub(r'}\s*', '}', js_content)
        js_content = re.sub(r'\(\s*', '(', js_content)
        js_content = re.sub(r'\s*\)', ')', js_content)
        js_content = re.sub(r'\[\s*', '[', js_content)
        js_content = re.sub(r'\s*\]', ']', js_content)
        
        # Remove leading/trailing whitespace
        js_content = js_content.strip()
        
        return js_content
    
    def compress_file(self, file_path: Path) -> Optional[Path]:
        """Compress a file using gzip"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            original_size = file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"Compressed {file_path.name}: {original_size} -> {compressed_size} bytes ({compression_ratio:.1f}% reduction)")
            
            return compressed_path
        except Exception as e:
            logger.error(f"Failed to compress {file_path}: {e}")
            return None
    
    def process_file(self, file_path: Path) -> Dict[str, any]:
        """Process a single file (minify and optionally compress)"""
        result = {
            'file': str(file_path),
            'original_size': file_path.stat().st_size,
            'minified_size': 0,
            'compressed_size': 0,
            'success': False,
            'error': None
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup
            backup_path = self.backup_dir / file_path.name
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Minify based on file type
            if file_path.suffix.lower() == '.css':
                minified_content = self.minify_css(content)
            elif file_path.suffix.lower() == '.js':
                minified_content = self.minify_js(content)
            else:
                logger.warning(f"Skipping unsupported file type: {file_path}")
                return result
            
            # Write minified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(minified_content)
            
            result['minified_size'] = len(minified_content.encode('utf-8'))
            result['success'] = True
            
            # Compress file
            compressed_path = self.compress_file(file_path)
            if compressed_path:
                result['compressed_size'] = compressed_path.stat().st_size
            
            # Calculate savings
            if result['success']:
                size_reduction = (1 - result['minified_size'] / result['original_size']) * 100
                logger.info(f"Minified {file_path.name}: {result['original_size']} -> {result['minified_size']} bytes ({size_reduction:.1f}% reduction)")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to process {file_path}: {e}")
        
        return result
    
    def find_asset_files(self) -> List[Path]:
        """Find all CSS and JavaScript files in the static directory"""
        asset_files = []
        
        for ext in ['*.css', '*.js']:
            asset_files.extend(self.static_dir.rglob(ext))
        
        # Filter out already minified files
        asset_files = [f for f in asset_files if not f.name.endswith('.min.css') and not f.name.endswith('.min.js')]
        
        return asset_files
    
    def process_all_assets(self, compress: bool = True) -> Dict[str, any]:
        """Process all asset files in the static directory"""
        asset_files = self.find_asset_files()
        
        if not asset_files:
            logger.warning("No asset files found to process")
            return {'processed': 0, 'successful': 0, 'failed': 0, 'results': []}
        
        logger.info(f"Found {len(asset_files)} asset files to process")
        
        results = []
        successful = 0
        failed = 0
        
        for file_path in asset_files:
            logger.info(f"Processing {file_path}")
            result = self.process_file(file_path)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        # Generate summary
        total_original_size = sum(r['original_size'] for r in results if r['success'])
        total_minified_size = sum(r['minified_size'] for r in results if r['success'])
        total_compressed_size = sum(r['compressed_size'] for r in results if r['success'])
        
        summary = {
            'processed': len(results),
            'successful': successful,
            'failed': failed,
            'total_original_size': total_original_size,
            'total_minified_size': total_minified_size,
            'total_compressed_size': total_compressed_size,
            'minification_savings': (1 - total_minified_size / total_original_size) * 100 if total_original_size > 0 else 0,
            'compression_savings': (1 - total_compressed_size / total_original_size) * 100 if total_original_size > 0 else 0,
            'results': results
        }
        
        logger.info(f"Processing complete: {successful} successful, {failed} failed")
        logger.info(f"Total size reduction: {summary['minification_savings']:.1f}% (minification) + {summary['compression_savings']:.1f}% (compression)")
        
        return summary
    
    def restore_backups(self):
        """Restore files from backup"""
        if not self.backup_dir.exists():
            logger.warning("No backup directory found")
            return
        
        backup_files = list(self.backup_dir.glob('*'))
        
        if not backup_files:
            logger.warning("No backup files found")
            return
        
        logger.info(f"Restoring {len(backup_files)} files from backup")
        
        for backup_file in backup_files:
            # Find original file
            original_file = self.static_dir / backup_file.name
            
            if original_file.exists():
                shutil.copy2(backup_file, original_file)
                logger.info(f"Restored {original_file}")
            else:
                logger.warning(f"Original file not found for {backup_file.name}")
        
        logger.info("Backup restoration complete")

def main():
    parser = argparse.ArgumentParser(description='Minify and compress static assets')
    parser.add_argument('--static-dir', default='static', help='Static files directory')
    parser.add_argument('--no-compress', action='store_true', help='Skip compression')
    parser.add_argument('--restore', action='store_true', help='Restore files from backup')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without making changes')
    
    args = parser.parse_args()
    
    minifier = AssetMinifier(args.static_dir)
    
    if args.restore:
        minifier.restore_backups()
        return
    
    if args.dry_run:
        asset_files = minifier.find_asset_files()
        logger.info(f"Would process {len(asset_files)} files:")
        for file_path in asset_files:
            logger.info(f"  {file_path}")
        return
    
    summary = minifier.process_all_assets(compress=not args.no_compress)
    
    # Print detailed results
    print("\nDetailed Results:")
    print("=" * 80)
    for result in summary['results']:
        if result['success']:
            size_reduction = (1 - result['minified_size'] / result['original_size']) * 100
            print(f"✓ {result['file']}: {result['original_size']} -> {result['minified_size']} bytes ({size_reduction:.1f}% reduction)")
        else:
            print(f"✗ {result['file']}: ERROR - {result['error']}")

if __name__ == '__main__':
    main()
