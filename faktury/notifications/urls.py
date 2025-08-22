from django.urls import path
from . import views

app_name = 'notifications'  # This line is important for namespacing

urlpatterns = [
    path('', views.notifications, name='list'),
    path('mark_as_read/<int:pk>/', views.mark_notification_read, name='mark_as_read'),
    # Add other URL patterns for notifications here
]