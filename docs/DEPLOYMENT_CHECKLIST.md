# 🚀 Lista kontrolna wdrożenia FaktuLove

## ⚠️ KRYTYCZNE - Przed wdrożeniem

### 1. 🔐 Bezpieczeństwo
- [ ] **Skopiuj i skonfiguruj .env**
  ```bash
  cp .env.example .env
  # Edytuj wszystkie wartości w .env
  ```

- [ ] **Wygeneruj nowy SECRET_KEY**
  ```python
  from django.core.management.utils import get_random_secret_key
  print(get_random_secret_key())
  ```

- [ ] **Ustaw DEBUG=False w produkcji**
- [ ] **Skonfiguruj ALLOWED_HOSTS**
- [ ] **Ustaw właściwe domeny w CSRF_TRUSTED_ORIGINS**

### 2. 📧 Email
- [ ] **Skonfiguruj ustawienia SMTP**
- [ ] **Przetestuj wysyłanie emaili**

### 3. 🗄️ Baza danych
- [ ] **Uruchom migracje**
  ```bash
  python manage.py migrate
  ```

- [ ] **Utwórz superusera**
  ```bash
  python manage.py createsuperuser
  ```

### 4. 📁 Pliki statyczne
- [ ] **Skonfiguruj obsługę plików statycznych**
  ```bash
  python manage.py collectstatic
  ```

## 🔧 Konfiguracja serwera

### 1. Web Server (Nginx/Apache)
- [ ] **Skonfiguruj reverse proxy**
- [ ] **Włącz SSL/TLS**
- [ ] **Ustaw właściwe nagłówki bezpieczeństwa**

### 2. WSGI Server (Gunicorn/uWSGI)
- [ ] **Skonfiguruj worker processes**
- [ ] **Ustaw timeout**
- [ ] **Skonfiguruj restart policy**

### 3. Database
- [ ] **Skonfiguruj connection pooling**
- [ ] **Ustaw backup strategy**
- [ ] **Zoptymalizuj parametry bazy**

## 🚀 Optymalizacje wydajności

### 1. Cache
- [ ] **Skonfiguruj Redis/Memcached**
- [ ] **Włącz cache dla views**
- [ ] **Skonfiguruj session storage w cache**

### 2. Monitoring
- [ ] **Skonfiguruj logi**
- [ ] **Ustaw monitoring wydajności**
- [ ] **Skonfiguruj alerty**

## ✅ Testy końcowe

### 1. Funkcjonalność
- [ ] **Test logowania**
- [ ] **Test tworzenia faktury**
- [ ] **Test generowania PDF**
- [ ] **Test wysyłania emaili**

### 2. Bezpieczeństwo
- [ ] **Test HTTPS**
- [ ] **Test nagłówków bezpieczeństwa**
- [ ] **Test CSRF protection**

### 3. Wydajność
- [ ] **Test ładowania strony (<2s)**
- [ ] **Test responsywności**
- [ ] **Test pod obciążeniem**

## 📋 Checklist wdrożeniowy

```bash
# 1. Sklonuj kod
git clone [repository-url]
cd faktulove

# 2. Utwórz środowisko wirtualne
python -m venv venv
source venv/bin/activate

# 3. Zainstaluj zależności
pip install -r requirements.txt

# 4. Skonfiguruj środowisko
cp .env.example .env
# EDYTUJ .env z właściwymi wartościami

# 5. Uruchom migracje
python manage.py migrate

# 6. Utwórz superusera
python manage.py createsuperuser

# 7. Zbierz pliki statyczne
python manage.py collectstatic

# 8. Test lokalny
python manage.py runserver

# 9. Uruchom w produkcji z Gunicorn
gunicorn faktulove.wsgi:application
```

## 🔍 Sprawdzenie bezpieczeństwa

```bash
# Uruchom check deployment
python manage.py check --deploy

# Sprawdź ustawienia bezpieczeństwa
python manage.py check --tag security
```

## 🆘 Rozwiązywanie problemów

### Problemy z bazą danych
```bash
# Reset migracji (tylko w razie potrzeby)
python manage.py migrate --fake-initial

# Sprawdź status migracji
python manage.py showmigrations
```

### Problemy z cache
```bash
# Wyczyść cache
python manage.py clear_cache
```

### Problemy z uprawnieniami
```bash
# Sprawdź uprawnienia plików
chmod -R 755 faktulove/
chmod -R 644 faktulove/media/
```

## 📞 Kontakt

W przypadku problemów:
1. Sprawdź logi aplikacji
2. Sprawdź dokumentację Django
3. Skontaktuj się z zespołem developerskim

---

**⚠️ PAMIĘTAJ: NIGDY NIE DEPLOYUJ BEZ TESTÓW I BACKUPU!**
