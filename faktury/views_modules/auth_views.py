"""
Authentication and user management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password

from ..forms import UserRegistrationForm, UserProfileForm
from ..models import UserProfile

import secrets
import string


def generate_password(length=12):
    """Generuje losowe hasło o podanej długości."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password


def send_credentials(email, username, password):
    """Wysyła e-mail z danymi do logowania."""
    subject = "Twoje dane do logowania do Systemu Faktur"
    message = f"""
    Witaj,

    Zostało utworzone dla Ciebie konto w Systemie Faktur.

    Twoje dane do logowania:

    Login: {username}
    Hasło: {password}

    Zaloguj się tutaj: {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}/accounts/login/

    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)


def register(request):
    """Basic user registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Konto dla {username} zostało utworzone! Możesz się teraz zalogować.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def user_profile(request, pk):
    """User profile view"""
    user = get_object_or_404(User, pk=pk)
    return render(request, 'faktury/user_profile.html', {'profile_user': user})


def rejestracja(request):
    """Enhanced user registration with profile"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Rejestracja przebiegła pomyślnie. Możesz się teraz zalogować.')
            return redirect('account_login')
    else:
        form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/register.html', {'form': form, 'profile_form': profile_form})
