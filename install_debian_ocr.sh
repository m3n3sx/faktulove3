#!/bin/bash
# Production OCR installation for Debian/Ubuntu
set -e

echo "🚀 Installing Production OCR Engines for FaktuLove (Debian)"
echo "=========================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    unzip \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl-dev \
    tk-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libopencv-dev \
    python3-opencv

# Install Tesseract OCR
echo "📖 Installing Tesseract OCR..."
sudo apt install -y tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng

# Verify Tesseract installation
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract installed: $(tesseract --version | head -n1)"
else
    echo "❌ Tesseract installation failed"
fi

# Upgrade pip
echo "🐍 Upgrading pip..."
python3 -m pip install --upgrade pip

# Install Python OCR packages
echo "🔍 Installing Python OCR packages..."
pip3 install --user \
    pytesseract>=0.3.10 \
    opencv-python>=4.8.0 \
    Pillow>=10.0.0 \
    numpy>=1.24.0 \
    scikit-image>=0.21.0 \
    pdf2image>=1.16.0 \
    requests>=2.31.0 \
    tqdm>=4.65.0

# Install EasyOCR (may take time)
echo "🤖 Installing EasyOCR (this may take a while)..."
pip3 install --user easyocr --timeout 600

# Try to install PaddleOCR (optional)
echo "🏓 Installing PaddleOCR (optional)..."
pip3 install --user paddlepaddle paddleocr || echo "⚠️ PaddleOCR installation failed (optional)"

# Create directories
echo "📁 Creating OCR directories..."
mkdir -p /home/admin/faktulove/ocr_models
mkdir -p /home/admin/faktulove/paddle_models
mkdir -p /home/admin/faktulove/uploads
mkdir -p /home/admin/faktulove/processed
mkdir -p /home/admin/faktulove/logs

# Set permissions
chown -R admin:admin /home/admin/faktulove/ 2>/dev/null || true
chmod -R 755 /home/admin/faktulove/

echo "✅ Production OCR setup completed!"
echo "🎯 Next steps:"
echo "1. Run: python3 setup_admin.py"
echo "2. Start OCR service: python3 production_ocr_service.py"
echo "3. Start Django: cd faktulove && python manage.py runserver 0.0.0.0:8000"