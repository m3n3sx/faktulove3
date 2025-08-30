#!/bin/bash

# 🔄 AKTUALIZACJA PRODUKCJI Z LOKALNEJ WERSJI
# Bezpieczna aktualizacja działającej aplikacji najnowszymi zmianami

set -e

SERVER="admin@ec2-13-60-160-136.eu-north-1.compute.amazonaws.com"
SSH_KEY="/home/ooxo/.ssh/klucz1.pem"
CURRENT_DIR="/home/admin/faktulove"
NEW_VERSION_DIR="/home/admin/faktulove/love/faktulove_now"
BACKUP_DIR="/home/admin/faktulove_backup_$(date +%Y%m%d_%H%M%S)"

echo "🚀 ROZPOCZYNAM AKTUALIZACJĘ PRODUKCJI Z LOKALNEJ WERSJI"
echo "=================================================="

# 1. Sprawdź status aktualnych usług
echo "📊 Sprawdzam status aktualnych usług..."
ssh -i $SSH_KEY $SERVER "ps aux | grep -E '(gunicorn|celery|python.*8001)' | grep -v grep | wc -l" || echo "Brak aktywnych procesów"

# 2. Utwórz backup aktualnej wersji
echo "💾 Tworzę backup aktualnej wersji..."
ssh -i $SSH_KEY $SERVER "
    cp -r $CURRENT_DIR $BACKUP_DIR
    echo '✅ Backup utworzony w: $BACKUP_DIR'
"

# 3. Zatrzymaj usługi
echo "⏹️ Zatrzymuję usługi..."
ssh -i $SSH_KEY $SERVER "
    pkill -f 'gunicorn.*faktulove' || echo 'Gunicorn już zatrzymany'
    pkill -f 'celery.*faktulove' || echo 'Celery już zatrzymany'  
    pkill -f 'python.*8001' || echo 'OCR service już zatrzymany'
    sleep 3
"

# 4. Zachowaj kluczowe pliki
echo "🔐 Zachowuję kluczowe pliki..."
ssh -i $SSH_KEY $SERVER "
    # Zachowaj bazę danych
    cp $CURRENT_DIR/db.sqlite3 /tmp/db_backup.sqlite3 2>/dev/null || echo 'Brak bazy SQLite'
    
    # Zachowaj pliki środowiskowe
    cp $CURRENT_DIR/.env /tmp/env_backup 2>/dev/null || echo 'Brak pliku .env'
    
    # Zachowaj logi
    cp -r $CURRENT_DIR/logs /tmp/logs_backup 2>/dev/null || echo 'Brak katalogu logs'
    
    # Zachowaj media
    cp -r $CURRENT_DIR/media /tmp/media_backup 2>/dev/null || echo 'Brak katalogu media'
    
    # Zachowaj venv
    cp -r $CURRENT_DIR/venv /tmp/venv_backup 2>/dev/null || echo 'Brak venv'
"

# 5. Usuń stare pliki (zachowaj strukturę)
echo "🗑️ Czyszczę stare pliki aplikacji..."
ssh -i $SSH_KEY $SERVER "
    cd $CURRENT_DIR
    
    # Usuń pliki aplikacji, ale zachowaj kluczowe katalogi
    rm -rf faktury/ faktury_projekt/ frontend/ static/ staticfiles/ 2>/dev/null || true
    rm -f manage.py requirements.txt *.py *.md *.sh 2>/dev/null || true
    
    echo '✅ Stare pliki aplikacji usunięte'
"

# 6. Skopiuj nową wersję
echo "📁 Kopiuję nową wersję aplikacji..."
ssh -i $SSH_KEY $SERVER "
    cd $NEW_VERSION_DIR
    
    # Kopiuj główne katalogi aplikacji
    cp -r faktury/ $CURRENT_DIR/
    cp -r faktury_projekt/ $CURRENT_DIR/
    cp -r frontend/ $CURRENT_DIR/ 2>/dev/null || echo 'Brak katalogu frontend'
    cp -r static/ $CURRENT_DIR/ 2>/dev/null || echo 'Brak katalogu static'
    cp -r tests/ $CURRENT_DIR/ 2>/dev/null || echo 'Brak katalogu tests'
    cp -r docs/ $CURRENT_DIR/ 2>/dev/null || echo 'Brak katalogu docs'
    cp -r scripts/ $CURRENT_DIR/ 2>/dev/null || echo 'Brak katalogu scripts'
    
    # Kopiuj pliki główne
    cp manage.py $CURRENT_DIR/
    cp requirements.txt $CURRENT_DIR/
    cp *.py $CURRENT_DIR/ 2>/dev/null || echo 'Brak dodatkowych plików .py'
    cp *.md $CURRENT_DIR/ 2>/dev/null || echo 'Brak plików .md'
    
    echo '✅ Nowa wersja skopiowana'
"

# 7. Przywróć zachowane pliki
echo "🔄 Przywracam zachowane pliki..."
ssh -i $SSH_KEY $SERVER "
    # Przywróć bazę danych
    cp /tmp/db_backup.sqlite3 $CURRENT_DIR/db.sqlite3 2>/dev/null || echo 'Brak bazy do przywrócenia'
    
    # Przywróć pliki środowiskowe
    cp /tmp/env_backup $CURRENT_DIR/.env 2>/dev/null || echo 'Brak .env do przywrócenia'
    
    # Przywróć logi
    cp -r /tmp/logs_backup $CURRENT_DIR/logs 2>/dev/null || mkdir -p $CURRENT_DIR/logs
    
    # Przywróć media
    cp -r /tmp/media_backup $CURRENT_DIR/media 2>/dev/null || mkdir -p $CURRENT_DIR/media
    
    # Przywróć venv
    cp -r /tmp/venv_backup $CURRENT_DIR/venv 2>/dev/null || echo 'Brak venv do przywrócenia'
    
    echo '✅ Kluczowe pliki przywrócone'
"

# 8. Aktualizuj zależności
echo "📦 Aktualizuję zależności..."
ssh -i $SSH_KEY $SERVER "
    cd $CURRENT_DIR
    source venv/bin/activate
    pip install -r requirements.txt --upgrade
    echo '✅ Zależności zaktualizowane'
"

# 9. Uruchom migracje
echo "🗄️ Uruchamiam migracje bazy danych..."
ssh -i $SSH_KEY $SERVER "
    cd $CURRENT_DIR
    source venv/bin/activate
    python manage.py makemigrations
    python manage.py migrate
    echo '✅ Migracje wykonane'
"

# 10. Zbierz pliki statyczne
echo "📄 Zbieram pliki statyczne..."
ssh -i $SSH_KEY $SERVER "
    cd $CURRENT_DIR
    source venv/bin/activate
    python manage.py collectstatic --noinput --clear
    echo '✅ Pliki statyczne zebrane'
"

# 11. Uruchom usługi ponownie
echo "🚀 Uruchamiam usługi ponownie..."
ssh -i $SSH_KEY $SERVER "
    cd $CURRENT_DIR
    source venv/bin/activate
    
    # Uruchom Gunicorn
    nohup gunicorn --bind 0.0.0.0:8000 --workers 3 faktulove.wsgi:application > logs/gunicorn.log 2>&1 &
    
    # Uruchom Celery
    nohup celery -A faktulove worker -l info -Q ocr,cleanup --concurrency=2 > logs/celery.log 2>&1 &
    
    # Uruchom OCR Service
    cd /home/admin
    nohup python3 simple_ocr_service.py > ocr_service.log 2>&1 &
    
    sleep 5
    echo '✅ Usługi uruchomione'
"

# 12. Sprawdź status
echo "🔍 Sprawdzam status usług..."
ssh -i $SSH_KEY $SERVER "
    echo 'Aktywne procesy:'
    ps aux | grep -E '(gunicorn|celery|python.*8001)' | grep -v grep
    
    echo ''
    echo 'Porty:'
    ss -tlnp | grep -E ':(8000|8001)'
    
    echo ''
    echo 'Test aplikacji:'
    curl -s -I https://faktulove.ooxo.pl/ | head -1
    
    echo ''
    echo 'Test OCR service:'
    curl -s http://localhost:8001/health | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"status\"])' 2>/dev/null || echo 'OCR service niedostępny'
"

# 13. Podsumowanie
echo ""
echo "🎉 AKTUALIZACJA ZAKOŃCZONA!"
echo "========================="
echo "✅ Backup utworzony w: $BACKUP_DIR"
echo "✅ Nowa wersja wdrożona"
echo "✅ Usługi uruchomione"
echo ""
echo "🌐 Aplikacja dostępna: https://faktulove.ooxo.pl/"
echo "🔧 Admin panel: https://faktulove.ooxo.pl/admin/"
echo "👤 Login: ooxo / ooxo"
echo ""
echo "📊 W przypadku problemów, przywróć backup:"
echo "ssh -i $SSH_KEY $SERVER 'rm -rf $CURRENT_DIR && mv $BACKUP_DIR $CURRENT_DIR'"

echo ""
echo "🔍 Sprawdź logi:"
echo "ssh -i $SSH_KEY $SERVER 'tail -f $CURRENT_DIR/logs/gunicorn.log'"