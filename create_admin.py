#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
django.setup()

from django.contrib.auth.models import User
from faktury.models import Firma

# Utwórz/zaktualizuj admina
username = 'ooxo'
password = 'ooxo'
email = 'admin@faktulove.ooxo.pl'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"✅ Admin {username} zaktualizowany")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✅ Admin {username} utworzony")

# Utwórz firmę dla admina
try:
    firma = Firma.objects.get(user=user)
    print(f"✅ Firma już istnieje: {firma.nazwa}")
except Firma.DoesNotExist:
    firma = Firma.objects.create(
        user=user,
        nazwa="FaktuLove Admin Company",
        adres="ul. Produkcyjna 1",
        kod_pocztowy="00-001",
        miasto="Warszawa",
        nip="1234567890",
        regon="123456789",
        email="admin@faktulove.ooxo.pl",
        telefon="+48 123 456 789"
    )
    print(f"✅ Firma utworzona: {firma.nazwa}")

print("🎯 Dane logowania:")
print(f"URL: https://faktulove.ooxo.pl/admin/")
print(f"Username: {username}")
print(f"Password: {password}")
