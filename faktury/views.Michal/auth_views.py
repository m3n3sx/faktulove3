### views/auth_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from faktury.models import User
from faktury.forms import UserRegistrationForm, UserProfileForm

def register(request):
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
def user_profile(request, pk=None):
    if pk is None:
        pk = request.user.pk
    user = get_object_or_404(User, pk=pk)
    return render(request, 'faktury/user_profile.html', {'profile_user': user})
