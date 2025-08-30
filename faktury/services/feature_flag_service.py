"""
Feature Flag Service for Design System Integration
Manages feature flags for gradual rollout and A/B testing
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
import hashlib

logger = logging.getLogger(__name__)

class FeatureFlagService:
    """Service for managing feature flags during rollout"""
    
    CACHE_PREFIX = "feature_flag"
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Design System Feature Flags
    DESIGN_SYSTEM_FLAGS = {
        "DESIGN_SYSTEM_BASIC_COMPONENTS": {
            "name": "Basic Design System Components",
            "description": "Enable basic components (Button, Input, etc.)",
            "category": "design_system",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "DESIGN_SYSTEM_FORM_COMPONENTS": {
            "name": "Form Components",
            "description": "Enable form-related design system components",
            "category": "design_system",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "DESIGN_SYSTEM_LAYOUT_COMPONENTS": {
            "name": "Layout Components",
            "description": "Enable layout components (Grid, Container, etc.)",
            "category": "design_system",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "DESIGN_SYSTEM_ADVANCED_COMPONENTS": {
            "name": "Advanced Components",
            "description": "Enable advanced components (Charts, Tables, etc.)",
            "category": "design_system",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "DESIGN_SYSTEM_THEMING": {
            "name": "Design System Theming",
            "description": "Enable theme switching and customization",
            "category": "design_system",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "DESIGN_SYSTEM_ACCESSIBILITY": {
            "name": "Accessibility Features",
            "description": "Enable accessibility enhancements",
            "category": "design_system",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "DESIGN_SYSTEM_PERFORMANCE_MONITORING": {
            "name": "Performance Monitoring",
            "description": "Enable performance monitoring for design system",
            "category": "design_system",
            "default_enabled": False,
            "rollout_percentage": 0
        }
    }
    
    # Polish Business Feature Flags
    POLISH_BUSINESS_FLAGS = {
        "POLISH_BUSINESS_NIP_VALIDATION": {
            "name": "NIP Validation",
            "description": "Enable Polish NIP validation component",
            "category": "polish_business",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "POLISH_BUSINESS_VAT_CALCULATOR": {
            "name": "VAT Calculator",
            "description": "Enable Polish VAT calculation component",
            "category": "polish_business",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "POLISH_BUSINESS_CURRENCY_FORMATTING": {
            "name": "Currency Formatting",
            "description": "Enable Polish currency formatting (PLN)",
            "category": "polish_business",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "POLISH_BUSINESS_DATE_FORMATTING": {
            "name": "Date Formatting",
            "description": "Enable Polish date formatting (DD.MM.YYYY)",
            "category": "polish_business",
            "default_enabled": False,
            "rollout_percentage": 0
        },
        "POLISH_BUSINESS_INVOICE_COMPLIANCE": {
            "name": "Invoice Compliance",
            "description": "Enable Polish invoice compliance checking",
            "category": "polish_business",
            "default_enabled": False,
            "rollout_percentage": 0
        }
    }
    
    def __init__(self):
        self.all_flags = {**self.DESIGN_SYSTEM_FLAGS, **self.POLISH_BUSINESS_FLAGS}
    
    def get_user_hash(self, user_id: int) -> str:
        """Generate consistent hash for user-based rollout"""
        user_string = f"{user_id}_{settings.SECRET_KEY}"
        return hashlib.md5(user_string.encode()).hexdigest()
    
    def is_user_in_rollout(self, user_id: int, percentage: int) -> bool:
        """Determine if user is included in rollout percentage"""
        if percentage >= 100:
            return True
        if percentage <= 0:
            return False
            
        user_hash = self.get_user_hash(user_id)
        # Use first 8 characters of hash to get a number 0-99
        hash_number = int(user_hash[:8], 16) % 100
        return hash_number < percentage
    
    def get_flag_config(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific flag"""
        cache_key = f"{self.CACHE_PREFIX}_config_{flag_name}"
        config = cache.get(cache_key)
        
        if config is None:
            # Get from database or use default
            config = self.all_flags.get(flag_name, {})
            
            # Override with any database settings
            try:
                from faktury.models import FeatureFlag
                db_flag = FeatureFlag.objects.filter(name=flag_name).first()
                if db_flag:
                    config.update({
                        "enabled": db_flag.enabled,
                        "rollout_percentage": db_flag.rollout_percentage,
                        "start_date": db_flag.start_date,
                        "end_date": db_flag.end_date
                    })
            except Exception as e:
                logger.warning(f"Could not load flag from database: {e}")
            
            cache.set(cache_key, config, self.CACHE_TIMEOUT)
        
        return config
    
    def is_flag_enabled(self, flag_name: str, user: Optional[User] = None, user_id: Optional[int] = None) -> bool:
        """Check if a feature flag is enabled for a user"""
        config = self.get_flag_config(flag_name)
        if not config:
            return False
        
        # Check if flag is globally disabled
        if not config.get("enabled", config.get("default_enabled", False)):
            return False
        
        # Check date range if specified
        now = datetime.now()
        start_date = config.get("start_date")
        end_date = config.get("end_date")
        
        if start_date and now < start_date:
            return False
        if end_date and now > end_date:
            return False
        
        # Check rollout percentage
        rollout_percentage = config.get("rollout_percentage", 0)
        if rollout_percentage >= 100:
            return True
        if rollout_percentage <= 0:
            return False
        
        # Determine user ID
        if user:
            user_id = user.id
        elif user_id is None:
            # No user context, use global percentage
            return rollout_percentage >= 100
        
        return self.is_user_in_rollout(user_id, rollout_percentage)
    
    def enable_flag(self, flag_name: str, percentage: int = 100, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> bool:
        """Enable a feature flag"""
        try:
            from faktury.models import FeatureFlag
            
            flag, created = FeatureFlag.objects.get_or_create(
                name=flag_name,
                defaults={
                    "enabled": True,
                    "rollout_percentage": percentage,
                    "start_date": start_date,
                    "end_date": end_date,
                    "description": self.all_flags.get(flag_name, {}).get("description", "")
                }
            )
            
            if not created:
                flag.enabled = True
                flag.rollout_percentage = percentage
                if start_date:
                    flag.start_date = start_date
                if end_date:
                    flag.end_date = end_date
                flag.save()
            
            # Clear cache
            cache_key = f"{self.CACHE_PREFIX}_config_{flag_name}"
            cache.delete(cache_key)
            
            logger.info(f"Feature flag {flag_name} enabled for {percentage}% of users")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable feature flag {flag_name}: {e}")
            return False
    
    def disable_flag(self, flag_name: str) -> bool:
        """Disable a feature flag"""
        try:
            from faktury.models import FeatureFlag
            
            flag = FeatureFlag.objects.filter(name=flag_name).first()
            if flag:
                flag.enabled = False
                flag.rollout_percentage = 0
                flag.save()
            
            # Clear cache
            cache_key = f"{self.CACHE_PREFIX}_config_{flag_name}"
            cache.delete(cache_key)
            
            logger.info(f"Feature flag {flag_name} disabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable feature flag {flag_name}: {e}")
            return False
    
    def disable_all_flags(self, category: Optional[str] = None) -> bool:
        """Disable all feature flags, optionally filtered by category"""
        try:
            from faktury.models import FeatureFlag
            
            flags_to_disable = []
            
            if category:
                # Filter by category
                for flag_name, config in self.all_flags.items():
                    if config.get("category") == category:
                        flags_to_disable.append(flag_name)
            else:
                flags_to_disable = list(self.all_flags.keys())
            
            # Disable flags in database
            FeatureFlag.objects.filter(name__in=flags_to_disable).update(
                enabled=False,
                rollout_percentage=0
            )
            
            # Clear cache for all flags
            for flag_name in flags_to_disable:
                cache_key = f"{self.CACHE_PREFIX}_config_{flag_name}"
                cache.delete(cache_key)
            
            logger.info(f"Disabled {len(flags_to_disable)} feature flags" + 
                       (f" in category {category}" if category else ""))
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable feature flags: {e}")
            return False
    
    def get_user_flags(self, user: Optional[User] = None, user_id: Optional[int] = None) -> Dict[str, bool]:
        """Get all feature flags status for a user"""
        flags_status = {}
        
        for flag_name in self.all_flags.keys():
            flags_status[flag_name] = self.is_flag_enabled(flag_name, user, user_id)
        
        return flags_status
    
    def get_flag_statistics(self) -> Dict[str, Any]:
        """Get statistics about feature flag usage"""
        try:
            from faktury.models import FeatureFlag
            from django.contrib.auth.models import User
            
            total_users = User.objects.count()
            enabled_flags = FeatureFlag.objects.filter(enabled=True)
            
            stats = {
                "total_flags": len(self.all_flags),
                "enabled_flags": enabled_flags.count(),
                "total_users": total_users,
                "flag_details": []
            }
            
            for flag in enabled_flags:
                estimated_users = int(total_users * flag.rollout_percentage / 100)
                stats["flag_details"].append({
                    "name": flag.name,
                    "rollout_percentage": flag.rollout_percentage,
                    "estimated_users": estimated_users,
                    "start_date": flag.start_date.isoformat() if flag.start_date else None,
                    "end_date": flag.end_date.isoformat() if flag.end_date else None
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get flag statistics: {e}")
            return {"error": str(e)}
    
    def validate_rollout_readiness(self) -> Dict[str, Any]:
        """Validate that the system is ready for rollout"""
        validation_results = {
            "ready": True,
            "checks": [],
            "warnings": [],
            "errors": []
        }
        
        # Check database connectivity
        try:
            from faktury.models import FeatureFlag
            FeatureFlag.objects.count()
            validation_results["checks"].append("✓ Database connectivity")
        except Exception as e:
            validation_results["errors"].append(f"✗ Database connectivity: {e}")
            validation_results["ready"] = False
        
        # Check cache connectivity
        try:
            cache.set("test_key", "test_value", 10)
            cache.get("test_key")
            cache.delete("test_key")
            validation_results["checks"].append("✓ Cache connectivity")
        except Exception as e:
            validation_results["errors"].append(f"✗ Cache connectivity: {e}")
            validation_results["ready"] = False
        
        # Check flag definitions
        if self.all_flags:
            validation_results["checks"].append(f"✓ {len(self.all_flags)} feature flags defined")
        else:
            validation_results["errors"].append("✗ No feature flags defined")
            validation_results["ready"] = False
        
        # Check for conflicting flags
        enabled_count = 0
        try:
            from faktury.models import FeatureFlag
            enabled_count = FeatureFlag.objects.filter(enabled=True).count()
        except:
            pass
        
        if enabled_count > 0:
            validation_results["warnings"].append(f"⚠ {enabled_count} flags already enabled")
        
        return validation_results

# Global instance
feature_flag_service = FeatureFlagService()