#!/usr/bin/env python3
"""
Skrypt do tworzenia użytkownika testowego dla FaktuLove
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
django.setup()

from django.contrib.auth.models import User
from faktury.models import Firma

def create_test_user():
    """Utwórz użytkownika testowego"""
    
    # Sprawdź czy użytkownik już istnieje
    username = 'testuser'
    email = 'test@faktulove.pl'
    password = 'testpass123'
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Użytkownik {username} już istnieje")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Utworzono użytkownika: {username}")
        print(f"   Email: {email}")
        print(f"   Hasło: {password}")
    
    # Sprawdź czy ma firmę
    try:
        firma = Firma.objects.get(user=user)
        print(f"✅ Firma już istnieje: {firma.nazwa}")
    except Firma.DoesNotExist:
        firma = Firma.objects.create(
            user=user,
            nazwa="Test Company Sp. z o.o.",
            adres="ul. Testowa 123",
            kod_pocztowy="00-001",
            miasto="Warszawa",
            nip="1234567890",
            regon="123456789",
            email="firma@test.pl",
            telefon="+48 123 456 789"
        )
        print(f"✅ Utworzono firmę: {firma.nazwa}")
    
    return user, firma

if __name__ == '__main__':
    user, firma = create_test_user()
    print("\n🎯 Dane do logowania:")
    print(f"Username: {user.username}")
    print(f"Password: testpass123")
    print(f"URL: http://localhost:8000/accounts/login/")
