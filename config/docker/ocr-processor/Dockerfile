# OCR Processor Docker Image
# Based on Ubuntu 22.04 with Tesseract 5.x and EasyOCR support

FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Python and pip
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    # Tesseract OCR 5.x with Polish language support
    tesseract-ocr \
    tesseract-ocr-pol \
    tesseract-ocr-eng \
    libtesseract-dev \
    # Additional language packs for better accuracy
    tesseract-ocr-script-latn \
    # Image processing libraries
    libopencv-dev \
    python3-opencv \
    # PDF processing
    poppler-utils \
    # Image manipulation
    imagemagick \
    libmagickwand-dev \
    # System utilities for model downloads
    wget \
    curl \
    unzip \
    ca-certificates \
    # Build tools for Python packages
    build-essential \
    pkg-config \
    # Additional image processing libraries
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick policy for PDF processing
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml

# Create app user for security
RUN useradd -m -u 1000 ocruser && chown -R ocruser:ocruser /app
USER ocruser

# Set up Python virtual environment
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and scripts first for better Docker layer caching
COPY --chown=ocruser:ocruser requirements-ocr-docker.txt .
COPY --chown=ocruser:ocruser docker/ocr-processor/healthcheck.sh /app/docker/ocr-processor/
RUN chmod +x /app/docker/ocr-processor/healthcheck.sh

# Install Python dependencies (CPU-optimized)
RUN pip install -r requirements-ocr-docker.txt

# Create directories for models and temporary files
RUN mkdir -p /app/models /app/temp /app/logs

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD /app/docker/ocr-processor/healthcheck.sh || exit 1

# Expose port for OCR service
EXPOSE 8001

# Default command
CMD ["python3", "-m", "faktury.services.ocr_server"]