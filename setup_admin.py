#!/usr/bin/env python3
"""
Setup admin user for FaktuLove production
"""
import os
import sys
import django

# Add the faktulove directory to Python path
sys.path.insert(0, '/home/admin/faktulove')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    from faktury.models import Firma
    
    print("🚀 Setting up admin user for FaktuLove...")
    
    # Create/update admin user
    username = 'ooxo'
    password = 'ooxo'
    email = 'admin@faktulove.ooxo.pl'
    
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        print(f"✅ Admin user '{username}' updated successfully")
    except User.DoesNotExist:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Admin user '{username}' created successfully")
    
    # Create company for admin if doesn't exist
    try:
        firma = Firma.objects.get(user=user)
        print(f"✅ Company already exists: {firma.nazwa}")
    except Firma.DoesNotExist:
        firma = Firma.objects.create(
            user=user,
            nazwa="FaktuLove Sp. z o.o.",
            adres="ul. Główna 1",
            kod_pocztowy="00-001",
            miasto="Warszawa",
            nip="1234567890",
            regon="123456789",
            email=email,
            telefon="+48 123 456 789"
        )
        print(f"✅ Company created: {firma.nazwa}")
    
    print("\n🎯 Login credentials:")
    print(f"URL: https://faktulove.ooxo.pl/admin/")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    
except Exception as e:
    print(f"❌ Error setting up admin: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)