"""
Feature Flag Service for OCR Migration
Manages gradual rollout from Google Cloud to open-source OCR
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Service for managing feature flags during OCR migration"""
    
    # Cache keys
    CACHE_KEY_PREFIX = "ocr_feature_flags"
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Default feature flags
    DEFAULT_FLAGS = {
        'use_opensource_ocr': False,
        'disable_google_cloud': False,
        'enable_ocr_fallback': True,
        'gradual_rollout_enabled': False,
        'rollout_percentage': 0,
        'rollout_user_groups': [],
        'enable_performance_monitoring': True,
        'enable_accuracy_comparison': False,
        'force_opensource_for_testing': False,
        'maintenance_mode': False,
    }
    
    # Rollout stages
    ROLLOUT_STAGES = {
        'stage_0': {'percentage': 0, 'description': 'No rollout - Google Cloud only'},
        'stage_1': {'percentage': 5, 'description': 'Pilot - 5% of users'},
        'stage_2': {'percentage': 15, 'description': 'Early adopters - 15% of users'},
        'stage_3': {'percentage': 35, 'description': 'Gradual rollout - 35% of users'},
        'stage_4': {'percentage': 60, 'description': 'Majority rollout - 60% of users'},
        'stage_5': {'percentage': 85, 'description': 'Near complete - 85% of users'},
        'stage_6': {'percentage': 100, 'description': 'Complete rollout - All users'},
    }
    
    def __init__(self):
        self.current_flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, Any]:
        """Load feature flags from cache, settings, or defaults"""
        # Try cache first
        cached_flags = cache.get(f"{self.CACHE_KEY_PREFIX}_current")
        if cached_flags:
            return cached_flags
        
        # Load from settings
        flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
        
        # Merge with defaults
        merged_flags = {**self.DEFAULT_FLAGS, **flags}
        
        # Cache the flags
        cache.set(f"{self.CACHE_KEY_PREFIX}_current", merged_flags, self.CACHE_TIMEOUT)
        
        return merged_flags
    
    def _save_flags(self, flags: Dict[str, Any]) -> None:
        """Save feature flags to cache"""
        self.current_flags = flags
        cache.set(f"{self.CACHE_KEY_PREFIX}_current", flags, self.CACHE_TIMEOUT)
        
        # Log flag changes
        logger.info(f"Feature flags updated: {flags}")
    
    def get_flag(self, flag_name: str, default: Any = None) -> Any:
        """Get a specific feature flag value"""
        return self.current_flags.get(flag_name, default)
    
    def set_flag(self, flag_name: str, value: Any) -> None:
        """Set a specific feature flag value"""
        self.current_flags[flag_name] = value
        self._save_flags(self.current_flags)
    
    def get_all_flags(self) -> Dict[str, Any]:
        """Get all current feature flags"""
        return self.current_flags.copy()
    
    def should_use_opensource_ocr(self, user_id: Optional[int] = None, 
                                 company_id: Optional[int] = None) -> bool:
        """
        Determine if open-source OCR should be used for this request
        
        Args:
            user_id: User ID for rollout calculation
            company_id: Company ID for rollout calculation
            
        Returns:
            bool: True if open-source OCR should be used
        """
        # Check maintenance mode
        if self.get_flag('maintenance_mode', False):
            logger.warning("OCR system in maintenance mode")
            return False
        
        # Check if forced for testing
        if self.get_flag('force_opensource_for_testing', False):
            return True
        
        # Check if completely disabled
        if not self.get_flag('use_opensource_ocr', False):
            return False
        
        # Check if Google Cloud is completely disabled
        if self.get_flag('disable_google_cloud', False):
            return True
        
        # Check gradual rollout
        if not self.get_flag('gradual_rollout_enabled', False):
            return self.get_flag('use_opensource_ocr', False)
        
        # Calculate rollout percentage
        rollout_percentage = self.get_flag('rollout_percentage', 0)
        
        if rollout_percentage >= 100:
            return True
        elif rollout_percentage <= 0:
            return False
        
        # Use deterministic rollout based on user/company ID
        rollout_id = user_id or company_id or 0
        rollout_hash = hash(f"ocr_rollout_{rollout_id}") % 100
        
        should_rollout = rollout_hash < rollout_percentage
        
        if should_rollout:
            logger.info(f"User/Company {rollout_id} selected for open-source OCR rollout")
        
        return should_rollout
    
    def should_enable_fallback(self) -> bool:
        """Check if OCR fallback should be enabled"""
        return self.get_flag('enable_ocr_fallback', True)
    
    def should_monitor_performance(self) -> bool:
        """Check if performance monitoring should be enabled"""
        return self.get_flag('enable_performance_monitoring', True)
    
    def should_compare_accuracy(self) -> bool:
        """Check if accuracy comparison should be enabled"""
        return self.get_flag('enable_accuracy_comparison', False)
    
    def get_current_rollout_stage(self) -> Dict[str, Any]:
        """Get current rollout stage information"""
        current_percentage = self.get_flag('rollout_percentage', 0)
        
        for stage_name, stage_info in self.ROLLOUT_STAGES.items():
            if current_percentage <= stage_info['percentage']:
                return {
                    'stage': stage_name,
                    'percentage': stage_info['percentage'],
                    'description': stage_info['description'],
                    'current_percentage': current_percentage
                }
        
        return {
            'stage': 'stage_6',
            'percentage': 100,
            'description': 'Complete rollout - All users',
            'current_percentage': current_percentage
        }
    
    def advance_rollout_stage(self) -> Dict[str, Any]:
        """Advance to the next rollout stage"""
        current_percentage = self.get_flag('rollout_percentage', 0)
        
        for stage_name, stage_info in self.ROLLOUT_STAGES.items():
            if current_percentage < stage_info['percentage']:
                self.set_flag('rollout_percentage', stage_info['percentage'])
                self.set_flag('gradual_rollout_enabled', True)
                
                logger.info(f"Advanced to rollout {stage_name}: {stage_info['percentage']}%")
                
                return {
                    'previous_percentage': current_percentage,
                    'new_percentage': stage_info['percentage'],
                    'stage': stage_name,
                    'description': stage_info['description']
                }
        
        # Already at maximum
        return {
            'previous_percentage': current_percentage,
            'new_percentage': current_percentage,
            'stage': 'stage_6',
            'description': 'Already at maximum rollout'
        }
    
    def rollback_rollout_stage(self) -> Dict[str, Any]:
        """Rollback to the previous rollout stage"""
        current_percentage = self.get_flag('rollout_percentage', 0)
        
        # Find previous stage
        previous_stage = None
        for stage_name, stage_info in self.ROLLOUT_STAGES.items():
            if stage_info['percentage'] < current_percentage:
                previous_stage = stage_info
            else:
                break
        
        if previous_stage:
            self.set_flag('rollout_percentage', previous_stage['percentage'])
            
            logger.warning(f"Rolled back to {previous_stage['percentage']}% rollout")
            
            return {
                'previous_percentage': current_percentage,
                'new_percentage': previous_stage['percentage'],
                'description': f"Rolled back to {previous_stage['percentage']}%"
            }
        else:
            # Disable rollout completely
            self.set_flag('rollout_percentage', 0)
            self.set_flag('gradual_rollout_enabled', False)
            
            logger.warning("Rolled back to 0% rollout - disabled gradual rollout")
            
            return {
                'previous_percentage': current_percentage,
                'new_percentage': 0,
                'description': "Rolled back to 0% - disabled gradual rollout"
            }
    
    def enable_maintenance_mode(self, reason: str = "Maintenance") -> None:
        """Enable maintenance mode"""
        self.set_flag('maintenance_mode', True)
        self.set_flag('maintenance_reason', reason)
        self.set_flag('maintenance_started', timezone.now().isoformat())
        
        logger.warning(f"OCR maintenance mode enabled: {reason}")
    
    def disable_maintenance_mode(self) -> None:
        """Disable maintenance mode"""
        self.set_flag('maintenance_mode', False)
        self.set_flag('maintenance_reason', None)
        self.set_flag('maintenance_ended', timezone.now().isoformat())
        
        logger.info("OCR maintenance mode disabled")
    
    def get_rollout_statistics(self) -> Dict[str, Any]:
        """Get rollout statistics"""
        return {
            'current_stage': self.get_current_rollout_stage(),
            'flags': self.get_all_flags(),
            'rollout_enabled': self.get_flag('gradual_rollout_enabled', False),
            'opensource_enabled': self.get_flag('use_opensource_ocr', False),
            'google_cloud_disabled': self.get_flag('disable_google_cloud', False),
            'maintenance_mode': self.get_flag('maintenance_mode', False),
            'last_updated': timezone.now().isoformat()
        }
    
    def validate_configuration(self) -> tuple[bool, list[str]]:
        """Validate feature flag configuration"""
        errors = []
        
        # Check for conflicting flags
        if (self.get_flag('disable_google_cloud', False) and 
            not self.get_flag('use_opensource_ocr', False)):
            errors.append("Google Cloud disabled but open-source OCR not enabled")
        
        # Check rollout percentage
        rollout_percentage = self.get_flag('rollout_percentage', 0)
        if not (0 <= rollout_percentage <= 100):
            errors.append(f"Invalid rollout percentage: {rollout_percentage}")
        
        # Check if gradual rollout is enabled but percentage is 0
        if (self.get_flag('gradual_rollout_enabled', False) and 
            rollout_percentage == 0):
            errors.append("Gradual rollout enabled but percentage is 0")
        
        return len(errors) == 0, errors


# Global instance
feature_flags = FeatureFlagService()