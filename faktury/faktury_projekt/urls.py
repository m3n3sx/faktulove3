from django.urls import path
from notifications import views

urlpatterns = [
    # inne URL-y
    path('notifications/', views.notifications_view, name='notifications'),
]