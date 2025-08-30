"""
API views for collecting user feedback during rollout
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from faktury.services.rollout_monitoring_service import rollout_monitoring_service
from faktury.services.feature_flag_service import feature_flag_service

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_rollout_feedback(request):
    """Submit user feedback about design system rollout"""
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['rating', 'category']
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"Missing required field: {field}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate rating
        rating = data.get('rating')
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return Response(
                {"error": "Rating must be an integer between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create feedback record
        from faktury.models import UserFeedback
        
        feedback = UserFeedback.objects.create(
            user=request.user,
            rating=rating,
            category=data.get('category'),
            comment=data.get('comment', ''),
            page_url=data.get('page_url', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            feature_flags_active=json.dumps(
                feature_flag_service.get_user_flags(user=request.user)
            ),
            created_at=datetime.now()
        )
        
        # Log the feedback event
        rollout_monitoring_service.log_rollout_event(
            'user_feedback_submitted',
            {
                'user_id': request.user.id,
                'rating': rating,
                'category': data.get('category'),
                'has_comment': bool(data.get('comment')),
                'page_url': data.get('page_url')
            }
        )
        
        return Response({
            "success": True,
            "feedback_id": feedback.id,
            "message": "Thank you for your feedback!"
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error submitting rollout feedback: {e}")
        return Response(
            {"error": "Failed to submit feedback"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rollout_metrics(request):
    """Get rollout metrics for monitoring dashboard"""
    try:
        # Check if user has permission to view metrics
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        dashboard_data = rollout_monitoring_service.generate_rollout_dashboard_data()
        
        return Response(dashboard_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting rollout metrics: {e}")
        return Response(
            {"error": "Failed to get metrics"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_feature_flags(request):
    """Get feature flags status for current user"""
    try:
        user = request.user if request.user.is_authenticated else None
        flags = feature_flag_service.get_user_flags(user=user)
        
        return Response({
            "feature_flags": flags,
            "user_authenticated": request.user.is_authenticated
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feature flags: {e}")
        return Response(
            {"error": "Failed to get feature flags"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_feature_flag(request):
    """Enable a feature flag (admin only)"""
    try:
        if not request.user.is_superuser:
            return Response(
                {"error": "Permission denied - admin required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        flag_name = data.get('flag')
        percentage = data.get('percentage', 100)
        
        if not flag_name:
            return Response(
                {"error": "Missing flag name"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = feature_flag_service.enable_flag(flag_name, percentage)
        
        if success:
            # Log the flag change
            rollout_monitoring_service.log_rollout_event(
                'feature_flag_enabled',
                {
                    'flag_name': flag_name,
                    'percentage': percentage,
                    'admin_user_id': request.user.id
                }
            )
            
            return Response({
                "success": True,
                "message": f"Feature flag {flag_name} enabled for {percentage}% of users"
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to enable feature flag"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Error enabling feature flag: {e}")
        return Response(
            {"error": "Failed to enable feature flag"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_feature_flag(request):
    """Disable a feature flag (admin only)"""
    try:
        if not request.user.is_superuser:
            return Response(
                {"error": "Permission denied - admin required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        flag_name = data.get('flag')
        
        if not flag_name:
            return Response(
                {"error": "Missing flag name"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = feature_flag_service.disable_flag(flag_name)
        
        if success:
            # Log the flag change
            rollout_monitoring_service.log_rollout_event(
                'feature_flag_disabled',
                {
                    'flag_name': flag_name,
                    'admin_user_id': request.user.id
                }
            )
            
            return Response({
                "success": True,
                "message": f"Feature flag {flag_name} disabled"
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to disable feature flag"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Error disabling feature flag: {e}")
        return Response(
            {"error": "Failed to disable feature flag"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_all_feature_flags(request):
    """Disable all feature flags (emergency rollback)"""
    try:
        if not request.user.is_superuser:
            return Response(
                {"error": "Permission denied - admin required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        category = data.get('category')  # Optional: disable only specific category
        
        success = feature_flag_service.disable_all_flags(category=category)
        
        if success:
            # Log the emergency rollback
            rollout_monitoring_service.log_rollout_event(
                'emergency_rollback',
                {
                    'category': category,
                    'admin_user_id': request.user.id,
                    'reason': data.get('reason', 'Emergency rollback')
                }
            )
            
            return Response({
                "success": True,
                "message": f"All feature flags{'in category ' + category if category else ''} disabled"
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to disable feature flags"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Error disabling all feature flags: {e}")
        return Response(
            {"error": "Failed to disable feature flags"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rollout_status(request):
    """Get current rollout status"""
    try:
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get feature flag statistics
        flag_stats = feature_flag_service.get_flag_statistics()
        
        # Get recent metrics
        dashboard_data = rollout_monitoring_service.generate_rollout_dashboard_data()
        
        # Get recent feedback summary
        feedback_summary = rollout_monitoring_service.get_user_feedback_summary(24)  # Last 24 hours
        
        rollout_status = {
            "flag_statistics": flag_stats,
            "current_metrics": {
                "error_rate": dashboard_data.get("error_rate", 0),
                "performance_score": dashboard_data.get("performance_score", 0),
                "user_satisfaction": dashboard_data.get("user_satisfaction", 0)
            },
            "feedback_summary": feedback_summary,
            "anomalies": dashboard_data.get("anomalies", []),
            "last_updated": datetime.now().isoformat()
        }
        
        return Response(rollout_status, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting rollout status: {e}")
        return Response(
            {"error": "Failed to get rollout status"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@require_http_methods(["POST"])
def log_feature_usage(request):
    """Log feature usage for analytics (can be called without authentication)"""
    try:
        data = json.loads(request.body)
        
        feature_name = data.get('feature_name')
        if not feature_name:
            return JsonResponse({"error": "Missing feature_name"}, status=400)
        
        # Create usage log
        from faktury.models import FeatureUsageLog
        
        FeatureUsageLog.objects.create(
            feature_name=feature_name,
            user_id=request.user.id if request.user.is_authenticated else None,
            session_id=request.session.session_key,
            page_url=data.get('page_url', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            timestamp=datetime.now()
        )
        
        return JsonResponse({"success": True})
        
    except Exception as e:
        logger.error(f"Error logging feature usage: {e}")
        return JsonResponse({"error": "Failed to log usage"}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_rollout_readiness(request):
    """Validate that system is ready for rollout"""
    try:
        if not request.user.is_superuser:
            return Response(
                {"error": "Permission denied - admin required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        validation_results = feature_flag_service.validate_rollout_readiness()
        
        return Response(validation_results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error validating rollout readiness: {e}")
        return Response(
            {"error": "Failed to validate readiness"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )