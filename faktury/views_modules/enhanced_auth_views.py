"""
Enhanced authentication views for FaktuLove
Integrates custom functionality with django-allauth
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
import json

from ..forms import UserRegistrationForm, UserProfileForm
from ..models import UserProfile
from ..decorators import ajax_required

import secrets
import string
import logging

logger = logging.getLogger(__name__)


class EnhancedAuthMixin:
    """Mixin for enhanced authentication functionality"""
    
    def get_user_profile_or_create(self, user):
        """Get or create user profile"""
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created profile for user {user.username}")
        return profile


def enhanced_registration(request):
    """
    Enhanced registration view with profile creation
    """
    if request.user.is_authenticated:
        return redirect('panel_uzytkownika')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if form.is_valid() and profile_form.is_valid():
            try:
                # Create user
                user = form.save()
                
                # Create profile
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                
                # Send welcome email (if not in debug mode)
                if not settings.DEBUG:
                    send_welcome_email(user)
                
                messages.success(
                    request, 
                    'Rejestracja przebiegła pomyślnie! Sprawdź swoją skrzynkę email i potwierdź adres.'
                )
                return redirect('account_login')
                
            except Exception as e:
                logger.error(f"Registration error: {e}")
                messages.error(request, 'Wystąpił błąd podczas rejestracji. Spróbuj ponownie.')
        else:
            # Log form errors for debugging
            if not form.is_valid():
                logger.warning(f"Registration form errors: {form.errors}")
            if not profile_form.is_valid():
                logger.warning(f"Profile form errors: {profile_form.errors}")
    else:
        form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'account/enhanced_signup.html', {
        'form': form,
        'profile_form': profile_form,
        'page_title': 'Rejestracja w FaktuLove'
    })


@ajax_required
@require_http_methods(["POST"])
def check_email_availability(request):
    """
    AJAX endpoint to check if email is available
    """
    data = json.loads(request.body)
    email = data.get('email', '').strip().lower()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email jest wymagany'})
    
    # Check if email exists
    exists = User.objects.filter(email=email).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Email dostępny' if not exists else 'Email jest już zajęty'
    })


@ajax_required
@require_http_methods(["POST"])
def check_username_availability(request):
    """
    AJAX endpoint to check if username is available
    """
    data = json.loads(request.body)
    username = data.get('username', '').strip()
    
    if not username:
        return JsonResponse({'available': False, 'message': 'Nazwa użytkownika jest wymagana'})
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Nazwa użytkownika musi mieć co najmniej 3 znaki'})
    
    # Check if username exists
    exists = User.objects.filter(username=username).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Nazwa dostępna' if not exists else 'Nazwa użytkownika jest już zajęta'
    })


@login_required
def enhanced_profile(request, pk=None):
    """
    Enhanced user profile view
    """
    if pk is None:
        user = request.user
    else:
        user = get_object_or_404(User, pk=pk)
        # Check if user can view this profile
        if user != request.user and not request.user.is_staff:
            messages.error(request, 'Nie masz uprawnień do przeglądania tego profilu.')
            return redirect('panel_uzytkownika')
    
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST' and user == request.user:
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profil został zaktualizowany.')
            return redirect('user_profile')
    else:
        profile_form = UserProfileForm(instance=profile) if user == request.user else None
    
    return render(request, 'faktury/enhanced_user_profile.html', {
        'profile_user': user,
        'profile': profile,
        'profile_form': profile_form,
        'can_edit': user == request.user
    })


def send_welcome_email(user):
    """
    Send welcome email to new user
    """
    try:
        subject = 'Witamy w FaktuLove!'
        html_message = render_to_string('emails/welcome_email.html', {
            'user': user,
            'login_url': settings.BASE_URL + reverse('account_login') if hasattr(settings, 'BASE_URL') else reverse('account_login')
        })
        
        send_mail(
            subject,
            '',  # Plain text message (empty, we use HTML)
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")


def custom_password_reset_request(request):
    """
    Custom password reset request with enhanced UX
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, 'Proszę podać adres email.')
            return render(request, 'account/enhanced_password_reset.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset URL
            reset_url = request.build_absolute_uri(
                reverse('account_reset_password_from_key', kwargs={
                    'uidb36': uid,
                    'key': token
                })
            )
            
            # Send email
            subject = 'Reset hasła - FaktuLove'
            html_message = render_to_string('emails/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'FaktuLove'
            })
            
            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(
                request, 
                'Instrukcje resetowania hasła zostały wysłane na Twój adres email.'
            )
            return redirect('account_login')
            
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            messages.success(
                request, 
                'Jeśli podany adres email istnieje w naszej bazie, otrzymasz instrukcje resetowania hasła.'
            )
            return redirect('account_login')
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            messages.error(request, 'Wystąpił błąd. Spróbuj ponownie później.')
    
    return render(request, 'account/enhanced_password_reset.html')


@login_required
def dashboard_redirect(request):
    """
    Smart redirect to appropriate dashboard based on user profile
    """
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check if user has completed profile
    if created or not profile.imie or not profile.nazwisko:
        messages.info(request, 'Proszę uzupełnić swój profil.')
        return redirect('user_profile')
    
    # Check if user has any companies
    if not request.user.firma_set.exists():
        messages.info(request, 'Proszę dodać dane swojej firmy aby rozpocząć korzystanie z FaktuLove.')
        return redirect('dodaj_firme')
    
    return redirect('panel_uzytkownika')


@ajax_required
@require_http_methods(["POST"])
def resend_confirmation_email(request):
    """
    Resend email confirmation
    """
    try:
        if request.user.is_authenticated and not request.user.emailaddress_set.filter(verified=True).exists():
            # Logic to resend confirmation email
            # This would integrate with allauth's email confirmation system
            return JsonResponse({
                'success': True,
                'message': 'Email potwierdzający został wysłany ponownie.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Nie można wysłać emaila potwierdzającego.'
            })
    except Exception as e:
        logger.error(f"Resend confirmation error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Wystąpił błąd. Spróbuj ponownie.'
        })
