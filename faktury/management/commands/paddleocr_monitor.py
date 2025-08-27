"""
Django management command for PaddleOCR monitoring and health checks
"""

import time
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor PaddleOCR service health and performance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Monitoring interval in seconds (default: 60)'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuous monitoring'
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Run single health check and exit'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--alert-threshold',
            type=int,
            default=3,
            help='Number of consecutive failures before alert (default: 3)'
        )
    
    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.verbose = options['verbose']
        self.interval = options['interval']
        self.continuous = options['continuous']
        self.check_only = options['check_only']
        self.alert_threshold = options['alert_threshold']
        
        # Initialize monitoring
        self.failure_count = 0
        self.last_alert_time = None
        
        self.stdout.write(
            self.style.SUCCESS('🔍 PaddleOCR Monitor Started')
        )
        
        if self.check_only:
            self.run_health_check()
        elif self.continuous:
            self.run_continuous_monitoring()
        else:
            self.run_single_check()
    
    def run_single_check(self):
        """Run a single comprehensive health check"""
        try:
            results = self.perform_health_checks()
            self.display_results(results)
            
            if not results['overall_health']:
                raise CommandError('Health check failed')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Health check error: {e}')
            )
            raise CommandError(str(e))
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        self.stdout.write(
            self.style.WARNING(f'Starting continuous monitoring (interval: {self.interval}s)')
        )
        
        try:
            while True:
                try:
                    results = self.perform_health_checks()
                    self.display_results(results)
                    
                    # Handle failures
                    if not results['overall_health']:
                        self.failure_count += 1
                        self.handle_failure(results)
                    else:
                        self.failure_count = 0
                    
                    # Wait for next check
                    time.sleep(self.interval)
                    
                except KeyboardInterrupt:
                    self.stdout.write(
                        self.style.WARNING('\nMonitoring stopped by user')
                    )
                    break
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Monitoring error: {e}')
                    )
                    time.sleep(self.interval)
                    
        except Exception as e:
            raise CommandError(f'Continuous monitoring failed: {e}')
    
    def run_health_check(self):
        """Run basic health check"""
        try:
            # Check PaddleOCR service availability
            from faktury.services.paddle_ocr_service import PaddleOCRService
            
            service = PaddleOCRService()
            is_available = service.validate_processor_availability()
            
            if is_available:
                self.stdout.write(
                    self.style.SUCCESS('✅ PaddleOCR service is healthy')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ PaddleOCR service is not available')
                )
                raise CommandError('PaddleOCR health check failed')
                
        except ImportError:
            self.stdout.write(
                self.style.ERROR('❌ PaddleOCR service not available (import error)')
            )
            raise CommandError('PaddleOCR service import failed')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ PaddleOCR health check failed: {e}')
            )
            raise CommandError(str(e))
    
    def perform_health_checks(self):
        """Perform comprehensive health checks"""
        results = {
            'timestamp': timezone.now(),
            'checks': {},
            'overall_health': True,
            'performance_metrics': {},
            'alerts': []
        }
        
        # Check PaddleOCR service
        results['checks']['paddleocr_service'] = self.check_paddleocr_service()
        
        # Check database connectivity
        results['checks']['database'] = self.check_database()
        
        # Check Redis connectivity
        results['checks']['redis'] = self.check_redis()
        
        # Check memory usage
        results['checks']['memory'] = self.check_memory_usage()
        
        # Check disk space
        results['checks']['disk_space'] = self.check_disk_space()
        
        # Get performance metrics
        results['performance_metrics'] = self.get_performance_metrics()
        
        # Determine overall health
        results['overall_health'] = all(
            check['status'] for check in results['checks'].values()
        )
        
        return results
    
    def check_paddleocr_service(self):
        """Check PaddleOCR service health"""
        try:
            from faktury.services.paddle_ocr_service import PaddleOCRService
            
            service = PaddleOCRService()
            is_available = service.validate_processor_availability()
            
            if is_available:
                # Get service info if available
                try:
                    service_info = service.get_service_info()
                    return {
                        'status': True,
                        'message': 'PaddleOCR service is healthy',
                        'details': service_info
                    }
                except:
                    return {
                        'status': True,
                        'message': 'PaddleOCR service is available',
                        'details': {}
                    }
            else:
                return {
                    'status': False,
                    'message': 'PaddleOCR service is not available',
                    'details': {}
                }
                
        except Exception as e:
            return {
                'status': False,
                'message': f'PaddleOCR service check failed: {e}',
                'details': {'error': str(e)}
            }
    
    def check_database(self):
        """Check database connectivity"""
        try:
            from django.db import connection
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            
            return {
                'status': True,
                'message': 'Database is accessible',
                'details': {}
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f'Database check failed: {e}',
                'details': {'error': str(e)}
            }
    
    def check_redis(self):
        """Check Redis connectivity"""
        try:
            from django.core.cache import cache
            
            # Test cache operation
            test_key = 'paddleocr_monitor_test'
            test_value = str(timezone.now())
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                return {
                    'status': True,
                    'message': 'Redis is accessible',
                    'details': {}
                }
            else:
                return {
                    'status': False,
                    'message': 'Redis test failed',
                    'details': {}
                }
                
        except Exception as e:
            return {
                'status': False,
                'message': f'Redis check failed: {e}',
                'details': {'error': str(e)}
            }
    
    def check_memory_usage(self):
        """Check system memory usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get PaddleOCR memory limits from settings
            paddleocr_config = getattr(settings, 'PADDLEOCR_CONFIG', {})
            memory_limit = paddleocr_config.get('max_memory_mb', 800)
            
            status = True
            message = f'Memory usage: {memory_percent:.1f}%'
            
            if memory_percent > 90:
                status = False
                message = f'Critical memory usage: {memory_percent:.1f}%'
            elif memory_percent > 80:
                message = f'High memory usage: {memory_percent:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'memory_percent': memory_percent,
                    'memory_limit_mb': memory_limit,
                    'available_mb': memory.available / 1024 / 1024
                }
            }
            
        except ImportError:
            return {
                'status': True,
                'message': 'Memory check skipped (psutil not available)',
                'details': {}
            }
        except Exception as e:
            return {
                'status': False,
                'message': f'Memory check failed: {e}',
                'details': {'error': str(e)}
            }
    
    def check_disk_space(self):
        """Check disk space usage"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage('.')
            used_percent = (used / total) * 100
            
            status = True
            message = f'Disk usage: {used_percent:.1f}%'
            
            if used_percent > 95:
                status = False
                message = f'Critical disk usage: {used_percent:.1f}%'
            elif used_percent > 85:
                message = f'High disk usage: {used_percent:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'used_percent': used_percent,
                    'free_gb': free / (1024**3),
                    'total_gb': total / (1024**3)
                }
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f'Disk check failed: {e}',
                'details': {'error': str(e)}
            }
    
    def get_performance_metrics(self):
        """Get performance metrics"""
        metrics = {}
        
        try:
            # Get PaddleOCR performance metrics if available
            from faktury.services.paddle_ocr_service import PaddleOCRService
            
            service = PaddleOCRService()
            
            # Try to get performance monitor stats
            if hasattr(service, 'performance_monitor') and service.performance_monitor:
                stats = service.performance_monitor.get_performance_stats()
                metrics['paddleocr_performance'] = stats
            
            # Try to get optimizer stats
            if hasattr(service, 'optimizer') and service.optimizer:
                optimizer_stats = service.optimizer.get_optimization_stats()
                metrics['paddleocr_optimization'] = optimizer_stats
            
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics
    
    def display_results(self, results):
        """Display health check results"""
        timestamp = results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        if results['overall_health']:
            self.stdout.write(
                self.style.SUCCESS(f'✅ [{timestamp}] All systems healthy')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ [{timestamp}] Health issues detected')
            )
        
        # Display individual check results
        if self.verbose or not results['overall_health']:
            for check_name, check_result in results['checks'].items():
                status_icon = '✅' if check_result['status'] else '❌'
                self.stdout.write(f'  {status_icon} {check_name}: {check_result["message"]}')
        
        # Display performance metrics if verbose
        if self.verbose and results['performance_metrics']:
            self.stdout.write('\n📊 Performance Metrics:')
            for metric_name, metric_data in results['performance_metrics'].items():
                if isinstance(metric_data, dict):
                    self.stdout.write(f'  {metric_name}: {len(metric_data)} items')
                else:
                    self.stdout.write(f'  {metric_name}: {metric_data}')
    
    def handle_failure(self, results):
        """Handle health check failures"""
        if self.failure_count >= self.alert_threshold:
            # Send alert if threshold reached
            current_time = timezone.now()
            
            # Avoid spamming alerts (minimum 1 hour between alerts)
            if (self.last_alert_time is None or 
                current_time - self.last_alert_time > timedelta(hours=1)):
                
                self.send_alert(results)
                self.last_alert_time = current_time
        
        self.stdout.write(
            self.style.WARNING(
                f'⚠️  Consecutive failures: {self.failure_count}/{self.alert_threshold}'
            )
        )
    
    def send_alert(self, results):
        """Send alert notification"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # Prepare alert message
            failed_checks = [
                name for name, check in results['checks'].items()
                if not check['status']
            ]
            
            subject = f'PaddleOCR Health Alert - {len(failed_checks)} checks failed'
            message = f"""
PaddleOCR Health Monitor Alert

Timestamp: {results['timestamp']}
Failed Checks: {', '.join(failed_checks)}
Consecutive Failures: {self.failure_count}

Failed Check Details:
"""
            
            for name in failed_checks:
                check = results['checks'][name]
                message += f"\n- {name}: {check['message']}"
            
            # Send email if configured
            if hasattr(settings, 'DEFAULT_FROM_EMAIL'):
                admin_emails = [admin[1] for admin in getattr(settings, 'ADMINS', [])]
                if admin_emails:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        admin_emails,
                        fail_silently=True
                    )
                    
                    self.stdout.write(
                        self.style.WARNING(f'📧 Alert sent to {len(admin_emails)} administrators')
                    )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send alert: {e}')
            )