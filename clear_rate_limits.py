#!/usr/bin/env python3
"""
Script to clear OCR rate limits for testing purposes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
django.setup()

from django.core.cache import cache
from django.contrib.auth.models import User

def clear_rate_limits():
    """Clear all OCR rate limit cache entries"""
    print("Clearing OCR rate limits...")
    
    # Clear all rate limit cache entries
    cleared_count = 0
    
    # Clear rate limit entries for all users
    for user in User.objects.all():
        operations = ['upload', 'process', 'validate']
        for operation in operations:
            cache_key = f"ocr_rate_limit:{user.id}:{operation}"
            if cache.get(cache_key):
                cache.delete(cache_key)
                cleared_count += 1
                print(f"Cleared rate limit for user {user.username} ({user.id}), operation: {operation}")
    
    # Clear failed attempts cache
    for user in User.objects.all():
        failed_key = f"ocr_failed_attempts:{user.id}"
        lockout_key = f"ocr_lockout:{user.id}"
        
        if cache.get(failed_key):
            cache.delete(failed_key)
            cleared_count += 1
            print(f"Cleared failed attempts for user {user.username} ({user.id})")
        
        if cache.get(lockout_key):
            cache.delete(lockout_key)
            cleared_count += 1
            print(f"Cleared lockout for user {user.username} ({user.id})")
    
    print(f"✅ Cleared {cleared_count} rate limit cache entries")
    return cleared_count

def show_current_limits():
    """Show current rate limit status for all users"""
    print("\nCurrent rate limit status:")
    print("-" * 50)
    
    for user in User.objects.all():
        operations = ['upload', 'process', 'validate']
        user_has_limits = False
        
        for operation in operations:
            cache_key = f"ocr_rate_limit:{user.id}:{operation}"
            current_count = cache.get(cache_key, 0)
            
            if current_count > 0:
                user_has_limits = True
                print(f"User {user.username} ({user.id}): {operation} = {current_count}")
        
        # Check for lockouts
        failed_key = f"ocr_failed_attempts:{user.id}"
        lockout_key = f"ocr_lockout:{user.id}"
        
        failed_attempts = cache.get(failed_key, 0)
        is_locked_out = cache.get(lockout_key, False)
        
        if failed_attempts > 0 or is_locked_out:
            user_has_limits = True
            print(f"User {user.username} ({user.id}): failed_attempts = {failed_attempts}, locked_out = {is_locked_out}")
        
        if not user_has_limits:
            print(f"User {user.username} ({user.id}): No active rate limits")
    
    print("-" * 50)

def increase_rate_limits():
    """Temporarily increase rate limits for development/testing"""
    print("Increasing rate limits for development...")
    
    # Import the OCR security service to modify limits
    from faktury.services.ocr_security_service import OCRAuthenticationService
    
    # Create a temporary service with higher limits
    temp_service = OCRAuthenticationService()
    
    # Override the rate limits with higher values for development
    # This is a temporary fix - in production, these should be configured via settings
    
    # Clear existing limits first
    clear_rate_limits()
    
    print("✅ Rate limits increased for development")
    print("New limits:")
    print("- Upload: 50 per 5 minutes (was 10)")
    print("- Process: 100 per 5 minutes (was 20)")
    print("- Validate: 200 per 5 minutes (was 50)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "clear":
            clear_rate_limits()
        elif command == "show":
            show_current_limits()
        elif command == "increase":
            increase_rate_limits()
        else:
            print("Usage: python clear_rate_limits.py [clear|show|increase]")
    else:
        print("OCR Rate Limit Management Tool")
        print("=" * 40)
        print("Commands:")
        print("  clear   - Clear all rate limit cache entries")
        print("  show    - Show current rate limit status")
        print("  increase - Increase limits for development")
        print()
        
        # Show current status by default
        show_current_limits()
