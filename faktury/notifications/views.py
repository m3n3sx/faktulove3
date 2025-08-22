from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.shortcuts import render
from django.db.models import Q
from .models import Notification

# Note: Make sure 'django.contrib.humanize' is added to INSTALLED_APPS in settings.py


@login_required
def notifications(request):
    # Get all notifications for the user
    all_notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    
    # Separate read and unread notifications
    unread_notifications = all_notifications.filter(status='UNREAD')
    read_notifications = all_notifications.filter(status='READ')
    
    return render(request, 'notifications/notifications.html', {
        'notifications': unread_notifications,
        'read_notifications': read_notifications
    })

@login_required
def mark_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.status = 'READ'
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'ok', 'id': pk})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Powiadomienie nie istnieje'}, status=404)

@login_required
def notifications_json(request):
    notifications = Notification.objects.filter(user=request.user, status='UNREAD')[:5]
    data = [{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'type': n.type,
        'timestamp': naturaltime(n.timestamp),
        'url': n.url if hasattr(n, 'url') else None
    } for n in notifications]
    return JsonResponse({
        'status': 'ok',
        'count': len(notifications),
        'notifications': data
    })

@login_required
def delete_notification(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Powiadomienie nie istnieje'}, status=404)
