#!/bin/bash
# Production OCR Installation Script

set -e

echo "🚀 Installing Production OCR Engines for FaktuLove"
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Tesseract OCR
echo "📖 Installing Tesseract OCR..."
sudo yum install -y epel-release
sudo yum install -y tesseract tesseract-langpack-pol tesseract-langpack-eng tesseract-devel

# Install Python development tools
echo "🐍 Installing Python development tools..."
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel python3-pip

# Install system dependencies for OCR
echo "📚 Installing OCR system dependencies..."
sudo yum install -y opencv opencv-devel
sudo yum install -y libffi-devel openssl-devel
sudo yum install -y libjpeg-turbo-devel zlib-devel
sudo yum install -y poppler-utils  # For PDF processing

# Install Python OCR packages
echo "🐍 Installing Python OCR packages..."
pip3 install --user --upgrade pip

# Core OCR packages
pip3 install --user pytesseract
pip3 install --user opencv-python
pip3 install --user Pillow
pip3 install --user numpy
pip3 install --user pdf2image
pip3 install --user scikit-image

# EasyOCR (może być wolne)
echo "🤖 Installing EasyOCR (this may take a while)..."
pip3 install --user easyocr

# PaddleOCR (opcjonalnie)
echo "🏓 Installing PaddleOCR (optional)..."
pip3 install --user paddlepaddle-cpu || echo "⚠️ PaddleOCR CPU failed, continuing..."
pip3 install --user paddleocr || echo "⚠️ PaddleOCR failed, continuing..."

# Create directories
echo "📁 Creating OCR directories..."
mkdir -p /home/admin/faktulove/paddle_models
mkdir -p /home/admin/faktulove/ocr_temp
mkdir -p /home/admin/faktulove/logs

# Set permissions
chmod 755 /home/admin/faktulove/paddle_models
chmod 755 /home/admin/faktulove/ocr_temp

echo "✅ Production OCR installation completed!"

# Test installations
echo "🧪 Testing OCR installations..."
python3 -c "
try:
    import pytesseract
    print('✅ Tesseract OK')
except Exception as e:
    print(f'❌ Tesseract: {e}')

try:
    import cv2
    print('✅ OpenCV OK')
except Exception as e:
    print(f'❌ OpenCV: {e}')

try:
    from PIL import Image
    print('✅ Pillow OK')
except Exception as e:
    print(f'❌ Pillow: {e}')

try:
    import easyocr
    print('✅ EasyOCR OK')
except Exception as e:
    print(f'❌ EasyOCR: {e}')

try:
    from paddleocr import PaddleOCR
    print('✅ PaddleOCR OK')
except Exception as e:
    print(f'❌ PaddleOCR: {e}')
"

echo "🎉 OCR setup completed!"
