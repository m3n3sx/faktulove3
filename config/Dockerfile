FROM python:3.11-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set locale for Polish language support
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install system dependencies including PaddleOCR requirements
RUN apt-get update && apt-get install -y \
    # Basic build tools
    build-essential \
    libpq-dev \
    libmagic1 \
    wget \
    curl \
    git \
    # PDF processing
    poppler-utils \
    # Tesseract OCR with Polish support
    tesseract-ocr \
    tesseract-ocr-pol \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    # OpenCV and image processing dependencies for PaddleOCR
    libopencv-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    liblcms2-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    # Additional image processing tools
    imagemagick \
    ghostscript \
    libmagickwand-dev \
    # System monitoring tools
    htop \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip and install wheel
RUN pip install --upgrade pip setuptools wheel

# Set work directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY requirements_ocr.txt .

# Install PyTorch CPU version first for better PaddleOCR compatibility
RUN pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_ocr.txt
RUN pip install --no-cache-dir google-cloud-documentai google-cloud-storage

# Create directories for PaddleOCR models and processing
RUN mkdir -p /app/paddle_models/det \
             /app/paddle_models/rec \
             /app/paddle_models/cls \
             /app/paddle_models/cache \
             /app/media/ocr_uploads \
             /app/logs \
             /app/.ocr_cache \
             /app/.ocr_result_cache

# Copy project files
COPY . .

# Set PaddleOCR environment variables
ENV PADDLEOCR_HOME=/app/paddle_models
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV OMP_NUM_THREADS=2
ENV PYTHONPATH=/app

# Pre-download PaddleOCR models to reduce startup time
RUN python -c "
import os
os.environ['PADDLEOCR_HOME'] = '/app/paddle_models'
try:
    from paddleocr import PaddleOCR
    # Initialize PaddleOCR with Polish and English support
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, 
                    det_model_dir='/app/paddle_models/det',
                    rec_model_dir='/app/paddle_models/rec',
                    cls_model_dir='/app/paddle_models/cls')
    print('PaddleOCR models downloaded successfully')
except Exception as e:
    print(f'PaddleOCR model download failed: {e}')
    # Continue anyway - models will be downloaded on first use
"

# Create health check script for PaddleOCR
RUN echo '#!/usr/bin/env python\n\
import sys\n\
import os\n\
import django\n\
\n\
# Setup Django\n\
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faktulove.settings")\n\
django.setup()\n\
\n\
def check_paddleocr():\n\
    try:\n\
        from faktury.services.paddle_ocr_service import PaddleOCRService\n\
        service = PaddleOCRService()\n\
        return service.validate_processor_availability()\n\
    except Exception as e:\n\
        print(f"PaddleOCR health check failed: {e}")\n\
        return False\n\
\n\
def check_database():\n\
    try:\n\
        from django.db import connection\n\
        cursor = connection.cursor()\n\
        cursor.execute("SELECT 1")\n\
        return True\n\
    except Exception as e:\n\
        print(f"Database health check failed: {e}")\n\
        return False\n\
\n\
if __name__ == "__main__":\n\
    checks = [\n\
        ("Database", check_database),\n\
        ("PaddleOCR", check_paddleocr)\n\
    ]\n\
    \n\
    for name, check in checks:\n\
        if not check():\n\
            print(f"Health check failed: {name}")\n\
            sys.exit(1)\n\
    \n\
    print("All health checks passed")\n\
    sys.exit(0)\n\
' > /app/healthcheck.py && chmod +x /app/healthcheck.py

# Health check configuration
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD python /app/healthcheck.py || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]