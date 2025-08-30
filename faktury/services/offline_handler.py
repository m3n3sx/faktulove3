"""
Offline Capability Handler for FaktuLove

Provides offline functionality and network status monitoring
with automatic synchronization when connection is restored.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class OfflineHandler:
    """
    Handles offline functionality and data synchronization
    
    Features:
    - Network status detection
    - Offline data storage
    - Automatic synchronization
    - Conflict resolution
    - User notifications
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.offline_storage_key = 'offline_data'
        self.sync_queue_key = 'sync_queue'
        
    def detect_network_status(self) -> Dict[str, Any]:
        """
        Detect current network connectivity status
        
        Returns:
            Dict containing network status information
        """
        try:
            # Try to make a simple HTTP request to check connectivity
            import urllib.request
            import socket
            
            # Set a short timeout for quick detection
            socket.setdefaulttimeout(3)
            
            # Try to connect to a reliable endpoint
            urllib.request.urlopen('https://www.google.com', timeout=3)
            
            return {
                'online': True,
                'status': 'connected',
                'message': 'Połączenie internetowe aktywne',
                'last_check': timezone.now().isoformat(),
                'latency': self._measure_latency()
            }
            
        except Exception as e:
            self.logger.warning(f"Network connectivity check failed: {e}")
            return {
                'online': False,
                'status': 'disconnected',
                'message': 'Brak połączenia internetowego',
                'last_check': timezone.now().isoformat(),
                'error': str(e)
            }
    
    def store_offline_data(self, user_id: int, operation: str, data: Dict[str, Any]) -> str:
        """
        Store data for offline processing
        
        Args:
            user_id: User ID
            operation: Type of operation (create_invoice, update_contractor, etc.)
            data: Data to store
            
        Returns:
            Unique ID for the stored operation
        """
        operation_id = f"offline_{user_id}_{int(timezone.now().timestamp())}_{operation}"
        
        offline_item = {
            'id': operation_id,
            'user_id': user_id,
            'operation': operation,
            'data': data,
            'timestamp': timezone.now().isoformat(),
            'status': 'pending',
            'retry_count': 0,
            'max_retries': 3
        }
        
        # Store in cache with extended expiration
        cache.set(f"{self.offline_storage_key}_{operation_id}", offline_item, 86400 * 7)  # 7 days
        
        # Add to sync queue
        self._add_to_sync_queue(user_id, operation_id)
        
        self.logger.info(f"Stored offline operation: {operation_id}")
        return operation_id
    
    def get_offline_data(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all offline data for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of offline operations
        """
        sync_queue = self._get_sync_queue(user_id)
        offline_items = []
        
        for operation_id in sync_queue:
            item = cache.get(f"{self.offline_storage_key}_{operation_id}")
            if item:
                offline_items.append(item)
        
        return offline_items
    
    def sync_offline_data(self, user_id: int) -> Dict[str, Any]:
        """
        Synchronize offline data when connection is restored
        
        Args:
            user_id: User ID
            
        Returns:
            Synchronization results
        """
        if not self.detect_network_status()['online']:
            return {
                'success': False,
                'message': 'Brak połączenia internetowego',
                'synced_count': 0,
                'failed_count': 0
            }
        
        offline_items = self.get_offline_data(user_id)
        synced_count = 0
        failed_count = 0
        sync_results = []
        
        for item in offline_items:
            try:
                result = self._sync_single_item(item)
                if result['success']:
                    synced_count += 1
                    self._remove_from_offline_storage(item['id'])
                else:
                    failed_count += 1
                    self._update_retry_count(item['id'])
                
                sync_results.append(result)
                
            except Exception as e:
                self.logger.error(f"Failed to sync item {item['id']}: {e}")
                failed_count += 1
                self._update_retry_count(item['id'])
        
        return {
            'success': True,
            'message': f'Zsynchronizowano {synced_count} operacji, {failed_count} nieudanych',
            'synced_count': synced_count,
            'failed_count': failed_count,
            'results': sync_results
        }
    
    def create_offline_fallback_response(self, request: HttpRequest, operation: str, data: Dict[str, Any]) -> JsonResponse:
        """
        Create offline fallback response for failed operations
        
        Args:
            request: HTTP request
            operation: Operation type
            data: Operation data
            
        Returns:
            JSON response with offline handling information
        """
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Operacja wymaga zalogowania',
                'offline_mode': False
            }, status=401)
        
        # Store data for offline processing
        operation_id = self.store_offline_data(request.user.id, operation, data)
        
        return JsonResponse({
            'success': True,
            'offline_mode': True,
            'operation_id': operation_id,
            'message': 'Operacja została zapisana i zostanie zsynchronizowana po przywróceniu połączenia',
            'operation': operation,
            'timestamp': timezone.now().isoformat(),
            'sync_info': {
                'auto_sync': True,
                'sync_interval': 30,  # seconds
                'manual_sync_available': True
            }
        })
    
    def get_sync_status(self, user_id: int) -> Dict[str, Any]:
        """
        Get synchronization status for user
        
        Args:
            user_id: User ID
            
        Returns:
            Sync status information
        """
        offline_items = self.get_offline_data(user_id)
        network_status = self.detect_network_status()
        
        pending_operations = [item for item in offline_items if item['status'] == 'pending']
        failed_operations = [item for item in offline_items if item['status'] == 'failed']
        
        return {
            'network_online': network_status['online'],
            'pending_count': len(pending_operations),
            'failed_count': len(failed_operations),
            'total_offline_operations': len(offline_items),
            'last_sync_attempt': self._get_last_sync_attempt(user_id),
            'auto_sync_enabled': True,
            'operations': offline_items
        }
    
    def _measure_latency(self) -> Optional[float]:
        """Measure network latency"""
        try:
            import time
            import urllib.request
            
            start_time = time.time()
            urllib.request.urlopen('https://www.google.com', timeout=5)
            end_time = time.time()
            
            return round((end_time - start_time) * 1000, 2)  # milliseconds
        except:
            return None
    
    def _add_to_sync_queue(self, user_id: int, operation_id: str) -> None:
        """Add operation to sync queue"""
        queue_key = f"{self.sync_queue_key}_{user_id}"
        sync_queue = cache.get(queue_key, [])
        
        if operation_id not in sync_queue:
            sync_queue.append(operation_id)
            cache.set(queue_key, sync_queue, 86400 * 7)  # 7 days
    
    def _get_sync_queue(self, user_id: int) -> List[str]:
        """Get sync queue for user"""
        queue_key = f"{self.sync_queue_key}_{user_id}"
        return cache.get(queue_key, [])
    
    def _sync_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize a single offline item
        
        Args:
            item: Offline item to sync
            
        Returns:
            Sync result
        """
        try:
            operation = item['operation']
            data = item['data']
            
            # Route to appropriate sync handler based on operation type
            if operation == 'create_invoice':
                return self._sync_create_invoice(data)
            elif operation == 'update_invoice':
                return self._sync_update_invoice(data)
            elif operation == 'create_contractor':
                return self._sync_create_contractor(data)
            elif operation == 'update_contractor':
                return self._sync_update_contractor(data)
            else:
                return {
                    'success': False,
                    'message': f'Nieznany typ operacji: {operation}',
                    'operation_id': item['id']
                }
                
        except Exception as e:
            self.logger.error(f"Failed to sync item {item['id']}: {e}")
            return {
                'success': False,
                'message': f'Błąd synchronizacji: {str(e)}',
                'operation_id': item['id']
            }
    
    def _sync_create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync create invoice operation"""
        try:
            from faktury.models import Faktura, Kontrahent, Firma
            
            # Get related objects
            kontrahent = Kontrahent.objects.get(id=data['kontrahent_id'])
            firma = Firma.objects.get(id=data['firma_id'])
            
            # Create invoice
            faktura = Faktura.objects.create(
                numer=data['numer'],
                kontrahent=kontrahent,
                firma=firma,
                data_wystawienia=data['data_wystawienia'],
                data_sprzedazy=data['data_sprzedazy'],
                termin_platnosci=data['termin_platnosci'],
                # Add other fields as needed
            )
            
            return {
                'success': True,
                'message': 'Faktura została utworzona',
                'object_id': faktura.id,
                'operation': 'create_invoice'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Błąd tworzenia faktury: {str(e)}',
                'operation': 'create_invoice'
            }
    
    def _sync_update_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync update invoice operation"""
        try:
            from faktury.models import Faktura
            
            faktura = Faktura.objects.get(id=data['invoice_id'])
            
            # Update fields
            for field, value in data['updates'].items():
                if hasattr(faktura, field):
                    setattr(faktura, field, value)
            
            faktura.save()
            
            return {
                'success': True,
                'message': 'Faktura została zaktualizowana',
                'object_id': faktura.id,
                'operation': 'update_invoice'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Błąd aktualizacji faktury: {str(e)}',
                'operation': 'update_invoice'
            }
    
    def _sync_create_contractor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync create contractor operation"""
        try:
            from faktury.models import Kontrahent
            
            kontrahent = Kontrahent.objects.create(
                nazwa=data['nazwa'],
                nip=data['nip'],
                adres=data['adres'],
                user_id=data['user_id'],
                # Add other fields as needed
            )
            
            return {
                'success': True,
                'message': 'Kontrahent został utworzony',
                'object_id': kontrahent.id,
                'operation': 'create_contractor'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Błąd tworzenia kontrahenta: {str(e)}',
                'operation': 'create_contractor'
            }
    
    def _sync_update_contractor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync update contractor operation"""
        try:
            from faktury.models import Kontrahent
            
            kontrahent = Kontrahent.objects.get(id=data['contractor_id'])
            
            # Update fields
            for field, value in data['updates'].items():
                if hasattr(kontrahent, field):
                    setattr(kontrahent, field, value)
            
            kontrahent.save()
            
            return {
                'success': True,
                'message': 'Kontrahent został zaktualizowany',
                'object_id': kontrahent.id,
                'operation': 'update_contractor'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Błąd aktualizacji kontrahenta: {str(e)}',
                'operation': 'update_contractor'
            }
    
    def _remove_from_offline_storage(self, operation_id: str) -> None:
        """Remove successfully synced item from offline storage"""
        cache.delete(f"{self.offline_storage_key}_{operation_id}")
        
        # Remove from all user sync queues (inefficient but simple)
        # In production, you'd want a more efficient approach
        for key in cache.keys(f"{self.sync_queue_key}_*"):
            queue = cache.get(key, [])
            if operation_id in queue:
                queue.remove(operation_id)
                cache.set(key, queue, 86400 * 7)
    
    def _update_retry_count(self, operation_id: str) -> None:
        """Update retry count for failed sync"""
        item = cache.get(f"{self.offline_storage_key}_{operation_id}")
        if item:
            item['retry_count'] += 1
            if item['retry_count'] >= item['max_retries']:
                item['status'] = 'failed'
            cache.set(f"{self.offline_storage_key}_{operation_id}", item, 86400 * 7)
    
    def _get_last_sync_attempt(self, user_id: int) -> Optional[str]:
        """Get timestamp of last sync attempt"""
        return cache.get(f"last_sync_attempt_{user_id}")
    
    def _set_last_sync_attempt(self, user_id: int) -> None:
        """Set timestamp of last sync attempt"""
        cache.set(f"last_sync_attempt_{user_id}", timezone.now().isoformat(), 86400)


# Global offline handler instance
offline_handler = OfflineHandler()