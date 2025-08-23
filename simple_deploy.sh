#!/bin/bash

echo "🚀 FaktuLove OCR - Production Deployment"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run from Django project root."
    exit 1
fi

echo "✅ Prerequisites check completed"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt --upgrade

echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "📂 Setting up media directories..."
mkdir -p media/documents media/uploads media/exports
chmod 755 media media/documents media/uploads media/exports

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure web server (Nginx/Apache)"
echo "2. Set up SSL certificates"
echo "3. Configure systemd services"  
echo "4. Start application services"
echo ""
echo "🎉 FaktuLove OCR is ready for production!"
