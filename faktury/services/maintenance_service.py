"""
Maintenance Service for database cleanup, optimization, and system maintenance.

Provides tools for database cleanup, optimization, backup/restore,
and maintenance mode functionality.
"""

import os
import shutil
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db import connection, transaction
from django.core.management import call_command
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
from django.core.files.storage import default_storage
from io import StringIO

from faktury.models import (
    Faktura, OCRResult, DocumentUpload, SystemHealth, 
    UserActivityLog, Notification
)

logger = logging.getLogger(__name__)


class MaintenanceService:
    """Service for system maintenance and optimization."""
    
    def __init__(self):
        self.maintenance_mode_key = 'system_maintenance_mode'
        self.backup_directory = getattr(settings, 'BACKUP_DIRECTORY', '/tmp/faktulove_backups')
        
    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """Clean up old data from the database."""
        cleanup_results = {
            'status': 'success',
            'cleaned_items': {},
            'errors': [],
            'total_freed_space': 0
        }
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        try:
            with transaction.atomic():
                # Clean up old OCR results
                old_ocr_results = OCRResult.objects.filter(
                    created_at__lt=cutoff_date,
                    confidence_score__lt=0.3  # Only clean up low-confidence results
                )
                ocr_count = old_ocr_results.count()
                old_ocr_results.delete()
                cleanup_results['cleaned_items']['ocr_results'] = ocr_count
                
                # Clean up old system health records (keep last 30 days)
                health_cutoff = timezone.now() - timedelta(days=30)
                old_health_records = SystemHealth.objects.filter(
                    timestamp__lt=health_cutoff
                )
                health_count = old_health_records.count()
                old_health_records.delete()
                cleanup_results['cleaned_items']['health_records'] = health_count
                
                # Clean up old user activity logs (keep last 60 days)
                activity_cutoff = timezone.now() - timedelta(days=60)
                old_activity_logs = UserActivityLog.objects.filter(
                    timestamp__lt=activity_cutoff
                )
                activity_count = old_activity_logs.count()
                old_activity_logs.delete()
                cleanup_results['cleaned_items']['activity_logs'] = activity_count
                
                # Clean up old notifications (keep last 30 days)
                notification_cutoff = timezone.now() - timedelta(days=30)
                old_notifications = Notification.objects.filter(
                    created_at__lt=notification_cutoff,
                    is_read=True
                )
                notification_count = old_notifications.count()
                old_notifications.delete()
                cleanup_results['cleaned_items']['notifications'] = notification_count
                
                # Clean up orphaned document uploads
                orphaned_uploads = DocumentUpload.objects.filter(
                    uploaded_at__lt=cutoff_date,
                    processing_status='failed'
                )
                upload_count = orphaned_uploads.count()
                
                # Delete associated files
                for upload in orphaned_uploads:
                    try:
                        if upload.file and default_storage.exists(upload.file.name):
                            default_storage.delete(upload.file.name)
                    except Exception as e:
                        logger.warning(f"Failed to delete file {upload.file.name}: {e}")
                
                orphaned_uploads.delete()
                cleanup_results['cleaned_items']['orphaned_uploads'] = upload_count
                
                logger.info(f"Database cleanup completed: {cleanup_results['cleaned_items']}")
                
        except Exception as e:
            cleanup_results['status'] = 'error'
            cleanup_results['errors'].append(f"Database cleanup failed: {str(e)}")
            logger.error(f"Database cleanup failed: {e}")
            
        return cleanup_results
    
    def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance."""
        optimization_results = {
            'status': 'success',
            'operations': [],
            'errors': [],
            'performance_improvement': {}
        }
        
        try:
            with connection.cursor() as cursor:
                # Get database engine
                db_engine = connection.vendor
                
                if db_engine == 'postgresql':
                    self._optimize_postgresql(cursor, optimization_results)
                elif db_engine == 'sqlite':
                    self._optimize_sqlite(cursor, optimization_results)
                else:
                    optimization_results['operations'].append(f"Optimization not implemented for {db_engine}")
                
                # Update table statistics
                if db_engine == 'postgresql':
                    cursor.execute("ANALYZE;")
                    optimization_results['operations'].append("Updated table statistics")
                
                logger.info(f"Database optimization completed: {optimization_results['operations']}")
                
        except Exception as e:
            optimization_results['status'] = 'error'
            optimization_results['errors'].append(f"Database optimization failed: {str(e)}")
            logger.error(f"Database optimization failed: {e}")
            
        return optimization_results
    
    def _optimize_postgresql(self, cursor, results):
        """PostgreSQL-specific optimizations."""
        try:
            # Vacuum and analyze tables
            cursor.execute("VACUUM ANALYZE;")
            results['operations'].append("Executed VACUUM ANALYZE")
            
            # Reindex tables if needed
            cursor.execute("REINDEX DATABASE faktulove;")
            results['operations'].append("Reindexed database")
            
        except Exception as e:
            results['errors'].append(f"PostgreSQL optimization error: {str(e)}")
    
    def _optimize_sqlite(self, cursor, results):
        """SQLite-specific optimizations."""
        try:
            # Vacuum database
            cursor.execute("VACUUM;")
            results['operations'].append("Executed VACUUM")
            
            # Analyze tables
            cursor.execute("ANALYZE;")
            results['operations'].append("Analyzed tables")
            
            # Optimize pragma settings
            cursor.execute("PRAGMA optimize;")
            results['operations'].append("Executed PRAGMA optimize")
            
        except Exception as e:
            results['errors'].append(f"SQLite optimization error: {str(e)}")
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create system backup."""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_results = {
            'status': 'success',
            'backup_name': backup_name,
            'backup_path': '',
            'backup_size': 0,
            'components': [],
            'errors': []
        }
        
        try:
            # Create backup directory
            backup_path = os.path.join(self.backup_directory, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            backup_results['backup_path'] = backup_path
            
            # Backup database
            db_backup_path = self._backup_database(backup_path)
            if db_backup_path:
                backup_results['components'].append('database')
            
            # Backup media files
            media_backup_path = self._backup_media_files(backup_path)
            if media_backup_path:
                backup_results['components'].append('media_files')
            
            # Backup configuration files
            config_backup_path = self._backup_configuration(backup_path)
            if config_backup_path:
                backup_results['components'].append('configuration')
            
            # Create backup manifest
            self._create_backup_manifest(backup_path, backup_results)
            
            # Calculate backup size
            backup_results['backup_size'] = self._calculate_directory_size(backup_path)
            
            logger.info(f"Backup created successfully: {backup_name}")
            
        except Exception as e:
            backup_results['status'] = 'error'
            backup_results['errors'].append(f"Backup creation failed: {str(e)}")
            logger.error(f"Backup creation failed: {e}")
            
        return backup_results
    
    def _backup_database(self, backup_path: str) -> Optional[str]:
        """Backup database to specified path."""
        try:
            db_config = settings.DATABASES['default']
            db_engine = db_config['ENGINE']
            
            if 'postgresql' in db_engine:
                return self._backup_postgresql(backup_path, db_config)
            elif 'sqlite' in db_engine:
                return self._backup_sqlite(backup_path, db_config)
            else:
                logger.warning(f"Database backup not implemented for {db_engine}")
                return None
                
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return None
    
    def _backup_postgresql(self, backup_path: str, db_config: Dict) -> str:
        """Backup PostgreSQL database."""
        backup_file = os.path.join(backup_path, 'database.sql')
        
        cmd = [
            'pg_dump',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', backup_file,
            '--no-password'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            return backup_file
        else:
            raise Exception(f"pg_dump failed: {result.stderr}")
    
    def _backup_sqlite(self, backup_path: str, db_config: Dict) -> str:
        """Backup SQLite database."""
        source_db = db_config['NAME']
        backup_file = os.path.join(backup_path, 'database.sqlite3')
        
        shutil.copy2(source_db, backup_file)
        return backup_file
    
    def _backup_media_files(self, backup_path: str) -> Optional[str]:
        """Backup media files."""
        try:
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if not media_root or not os.path.exists(media_root):
                return None
            
            media_backup_path = os.path.join(backup_path, 'media')
            shutil.copytree(media_root, media_backup_path)
            return media_backup_path
            
        except Exception as e:
            logger.error(f"Media files backup failed: {e}")
            return None
    
    def _backup_configuration(self, backup_path: str) -> Optional[str]:
        """Backup configuration files."""
        try:
            config_backup_path = os.path.join(backup_path, 'config')
            os.makedirs(config_backup_path, exist_ok=True)
            
            # Backup settings files
            config_files = [
                'faktulove/settings.py',
                '.env',
                'requirements.txt'
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, config_backup_path)
            
            return config_backup_path
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
            return None
    
    def _create_backup_manifest(self, backup_path: str, backup_info: Dict):
        """Create backup manifest file."""
        manifest = {
            'backup_name': backup_info['backup_name'],
            'created_at': datetime.now().isoformat(),
            'components': backup_info['components'],
            'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            'database_engine': settings.DATABASES['default']['ENGINE']
        }
        
        manifest_path = os.path.join(backup_path, 'manifest.json')
        with open(manifest_path, 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of directory in bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size
    
    def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """Restore system from backup."""
        restore_results = {
            'status': 'success',
            'backup_name': backup_name,
            'restored_components': [],
            'errors': []
        }
        
        try:
            backup_path = os.path.join(self.backup_directory, backup_name)
            
            if not os.path.exists(backup_path):
                raise Exception(f"Backup {backup_name} not found")
            
            # Load backup manifest
            manifest_path = os.path.join(backup_path, 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    import json
                    manifest = json.load(f)
            else:
                raise Exception("Backup manifest not found")
            
            # Restore database
            if 'database' in manifest['components']:
                if self._restore_database(backup_path):
                    restore_results['restored_components'].append('database')
            
            # Restore media files
            if 'media_files' in manifest['components']:
                if self._restore_media_files(backup_path):
                    restore_results['restored_components'].append('media_files')
            
            logger.info(f"Backup restored successfully: {backup_name}")
            
        except Exception as e:
            restore_results['status'] = 'error'
            restore_results['errors'].append(f"Backup restore failed: {str(e)}")
            logger.error(f"Backup restore failed: {e}")
            
        return restore_results
    
    def _restore_database(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            db_config = settings.DATABASES['default']
            db_engine = db_config['ENGINE']
            
            if 'postgresql' in db_engine:
                return self._restore_postgresql(backup_path, db_config)
            elif 'sqlite' in db_engine:
                return self._restore_sqlite(backup_path, db_config)
            else:
                logger.warning(f"Database restore not implemented for {db_engine}")
                return False
                
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    def _restore_postgresql(self, backup_path: str, db_config: Dict) -> bool:
        """Restore PostgreSQL database."""
        backup_file = os.path.join(backup_path, 'database.sql')
        
        if not os.path.exists(backup_file):
            return False
        
        cmd = [
            'psql',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', backup_file
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        return result.returncode == 0
    
    def _restore_sqlite(self, backup_path: str, db_config: Dict) -> bool:
        """Restore SQLite database."""
        backup_file = os.path.join(backup_path, 'database.sqlite3')
        
        if not os.path.exists(backup_file):
            return False
        
        target_db = db_config['NAME']
        shutil.copy2(backup_file, target_db)
        return True
    
    def _restore_media_files(self, backup_path: str) -> bool:
        """Restore media files from backup."""
        try:
            media_backup_path = os.path.join(backup_path, 'media')
            
            if not os.path.exists(media_backup_path):
                return False
            
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if not media_root:
                return False
            
            # Remove existing media files
            if os.path.exists(media_root):
                shutil.rmtree(media_root)
            
            # Restore from backup
            shutil.copytree(media_backup_path, media_root)
            return True
            
        except Exception as e:
            logger.error(f"Media files restore failed: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        
        try:
            if not os.path.exists(self.backup_directory):
                return backups
            
            for backup_name in os.listdir(self.backup_directory):
                backup_path = os.path.join(self.backup_directory, backup_name)
                
                if os.path.isdir(backup_path):
                    backup_info = {
                        'name': backup_name,
                        'path': backup_path,
                        'size': self._calculate_directory_size(backup_path),
                        'created_at': datetime.fromtimestamp(
                            os.path.getctime(backup_path)
                        ).isoformat(),
                        'components': []
                    }
                    
                    # Load manifest if available
                    manifest_path = os.path.join(backup_path, 'manifest.json')
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, 'r') as f:
                                import json
                                manifest = json.load(f)
                                backup_info.update(manifest)
                        except Exception:
                            pass
                    
                    backups.append(backup_info)
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            
        return backups
    
    def enable_maintenance_mode(self, message: str = "System maintenance in progress") -> bool:
        """Enable maintenance mode."""
        try:
            maintenance_info = {
                'enabled': True,
                'message': message,
                'enabled_at': timezone.now().isoformat(),
                'enabled_by': 'system'
            }
            
            cache.set(self.maintenance_mode_key, maintenance_info, timeout=None)
            logger.info("Maintenance mode enabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable maintenance mode: {e}")
            return False
    
    def disable_maintenance_mode(self) -> bool:
        """Disable maintenance mode."""
        try:
            cache.delete(self.maintenance_mode_key)
            logger.info("Maintenance mode disabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable maintenance mode: {e}")
            return False
    
    def is_maintenance_mode_enabled(self) -> Dict[str, Any]:
        """Check if maintenance mode is enabled."""
        maintenance_info = cache.get(self.maintenance_mode_key)
        
        if maintenance_info:
            return maintenance_info
        else:
            return {'enabled': False}
    
    def collect_diagnostic_info(self) -> Dict[str, Any]:
        """Collect comprehensive diagnostic information."""
        diagnostic_info = {
            'timestamp': timezone.now().isoformat(),
            'system_info': {},
            'database_info': {},
            'application_info': {},
            'performance_info': {},
            'errors': []
        }
        
        try:
            # System information
            diagnostic_info['system_info'] = {
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
                'debug_mode': settings.DEBUG,
                'timezone': str(settings.TIME_ZONE),
                'language_code': settings.LANGUAGE_CODE
            }
            
            # Database information
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0] if connection.vendor == 'postgresql' else 'SQLite'
                
                diagnostic_info['database_info'] = {
                    'engine': connection.vendor,
                    'version': db_version,
                    'connection_count': len(connection.queries) if settings.DEBUG else 'N/A'
                }
            
            # Application information
            diagnostic_info['application_info'] = {
                'total_invoices': Faktura.objects.count(),
                'total_ocr_results': OCRResult.objects.count(),
                'recent_uploads': DocumentUpload.objects.filter(
                    uploaded_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'failed_uploads': DocumentUpload.objects.filter(
                    processing_status='failed'
                ).count()
            }
            
            # Performance information
            recent_health = SystemHealth.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=1)
            ).aggregate(
                avg_response_time=models.Avg('response_time'),
                total_errors=models.Sum('error_count')
            )
            
            diagnostic_info['performance_info'] = {
                'avg_response_time_1h': recent_health.get('avg_response_time', 0),
                'total_errors_1h': recent_health.get('total_errors', 0),
                'cache_backend': str(cache.__class__.__name__)
            }
            
        except Exception as e:
            diagnostic_info['errors'].append(f"Failed to collect diagnostic info: {str(e)}")
            logger.error(f"Diagnostic info collection failed: {e}")
            
        return diagnostic_info