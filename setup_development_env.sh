#!/bin/bash

# ============================================================================
# Development Environment Setup Script for FaktuLove OCR
# ============================================================================
# This script sets up the complete development environment for FaktuLove OCR
# including Docker, Redis, PostgreSQL, and all dependencies
# ============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
    else
        print_warning "Docker is not installed. Install from: https://docs.docker.com/get-docker/"
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed"
    else
        print_warning "Docker Compose is not installed"
    fi
}

# Create Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Python environment ready"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Ensure we're in virtual environment
    source venv/bin/activate
    
    # Install from requirements.txt
    pip install -r requirements.txt
    
    # Install additional OCR-specific dependencies
    pip install google-cloud-documentai google-cloud-storage
    
    print_success "All dependencies installed"
}

# Create Docker Compose file
create_docker_compose() {
    print_status "Creating Docker Compose configuration..."
    
    cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: faktulove_postgres
    environment:
      POSTGRES_DB: faktulove_db
      POSTGRES_USER: faktulove_user
      POSTGRES_PASSWORD: faktulove_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faktulove_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: faktulove_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  celery_worker:
    build: .
    container_name: faktulove_celery_worker
    command: celery -A faktury_projekt worker -l info -Q ocr,cleanup
    environment:
      - DJANGO_SETTINGS_MODULE=faktury_projekt.settings
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://faktulove_user:faktulove_password@postgres:5432/faktulove_db
    volumes:
      - .:/app
      - ./media:/app/media
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  celery_beat:
    build: .
    container_name: faktulove_celery_beat
    command: celery -A faktury_projekt beat -l info
    environment:
      - DJANGO_SETTINGS_MODULE=faktury_projekt.settings
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://faktulove_user:faktulove_password@postgres:5432/faktulove_db
    volumes:
      - .:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  flower:
    build: .
    container_name: faktulove_flower
    command: celery -A faktury_projekt flower
    environment:
      - DJANGO_SETTINGS_MODULE=faktury_projekt.settings
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "5555:5555"
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF
    
    print_success "Docker Compose configuration created"
}

# Create Dockerfile
create_dockerfile() {
    print_status "Creating Dockerfile..."
    
    cat > Dockerfile <<'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-pol \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir google-cloud-documentai google-cloud-storage

# Copy project files
COPY . .

# Create media directories
RUN mkdir -p media/ocr_uploads

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF
    
    print_success "Dockerfile created"
}

# Create .env template
create_env_template() {
    print_status "Creating .env template..."
    
    if [ ! -f .env ]; then
        cat > .env <<'EOF'
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (for Docker)
DATABASE_URL=postgresql://faktulove_user:faktulove_password@localhost:5432/faktulove_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=faktulove-ocr
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
DOCUMENT_AI_PROCESSOR_ID=your-processor-id-here

# GUS API Configuration
GUS_API_KEY=your-gus-api-key-here

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
EOF
        print_success ".env template created"
        print_warning "Please update .env file with your actual configuration values"
    else
        print_warning ".env file already exists"
    fi
}

# Create media directories
create_media_dirs() {
    print_status "Creating media directories..."
    
    mkdir -p media/ocr_uploads
    mkdir -p media/avatars
    mkdir -p media/logos
    
    # Set permissions
    chmod 755 media
    chmod 755 media/ocr_uploads
    chmod 755 media/avatars
    chmod 755 media/logos
    
    print_success "Media directories created"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Start PostgreSQL container if using Docker
    if command -v docker-compose &> /dev/null; then
        print_status "Starting PostgreSQL container..."
        docker-compose up -d postgres
        
        # Wait for PostgreSQL to be ready
        print_status "Waiting for PostgreSQL to be ready..."
        sleep 10
    fi
    
    # Run migrations
    print_status "Running database migrations..."
    source venv/bin/activate
    python manage.py makemigrations
    python manage.py migrate
    
    print_success "Database setup complete"
}

# Create development scripts
create_dev_scripts() {
    print_status "Creating development helper scripts..."
    
    # Create start script
    cat > start_dev.sh <<'EOF'
#!/bin/bash
# Start all development services

echo "Starting development environment..."

# Start Docker services
docker-compose up -d postgres redis

# Wait for services
sleep 5

# Activate virtual environment
source venv/bin/activate

# Start Celery worker in background
celery -A faktury_projekt worker -l info -Q ocr,cleanup &
CELERY_WORKER_PID=$!

# Start Celery beat in background
celery -A faktury_projekt beat -l info &
CELERY_BEAT_PID=$!

# Start Django development server
python manage.py runserver

# Cleanup on exit
trap "kill $CELERY_WORKER_PID $CELERY_BEAT_PID; docker-compose down" EXIT
EOF
    
    chmod +x start_dev.sh
    
    # Create stop script
    cat > stop_dev.sh <<'EOF'
#!/bin/bash
# Stop all development services

echo "Stopping development environment..."

# Stop Celery processes
pkill -f "celery worker"
pkill -f "celery beat"

# Stop Docker services
docker-compose down

echo "Development environment stopped"
EOF
    
    chmod +x stop_dev.sh
    
    # Create test script
    cat > run_tests.sh <<'EOF'
#!/bin/bash
# Run all tests

source venv/bin/activate

echo "Running Django tests..."
python manage.py test faktury.tests

echo "Running OCR integration tests..."
python manage.py test faktury.tests.test_ocr_integration

echo "Tests complete"
EOF
    
    chmod +x run_tests.sh
    
    print_success "Development scripts created"
}

# Display summary
display_summary() {
    echo ""
    echo "============================================================================"
    echo "                 DEVELOPMENT ENVIRONMENT SETUP COMPLETE!"
    echo "============================================================================"
    echo ""
    echo "Environment Details:"
    echo "- Python virtual environment: ./venv"
    echo "- Docker services: PostgreSQL, Redis"
    echo "- Media directories: ./media/ocr_uploads"
    echo ""
    echo "Quick Start Commands:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Start all services: ./start_dev.sh"
    echo "3. Stop all services: ./stop_dev.sh"
    echo "4. Run tests: ./run_tests.sh"
    echo ""
    echo "Docker Commands:"
    echo "- Start services: docker-compose up -d"
    echo "- View logs: docker-compose logs -f"
    echo "- Stop services: docker-compose down"
    echo ""
    echo "Celery Monitoring:"
    echo "- Flower dashboard: http://localhost:5555"
    echo "- Redis CLI: docker exec -it faktulove_redis redis-cli"
    echo ""
    echo "Next Steps:"
    echo "1. Update .env file with your configuration"
    echo "2. Run ./setup_google_cloud.sh to configure Google Cloud"
    echo "3. Start development server with ./start_dev.sh"
    echo "4. Access application at http://localhost:8000"
    echo ""
    echo "============================================================================"
}

# Main execution
main() {
    echo "============================================================================"
    echo "        FAKTULOVE OCR DEVELOPMENT ENVIRONMENT SETUP"
    echo "============================================================================"
    echo ""
    
    # Check requirements
    check_requirements
    
    # Setup Python environment
    setup_python_env
    install_dependencies
    
    # Create Docker configuration
    create_docker_compose
    create_dockerfile
    
    # Create configuration files
    create_env_template
    
    # Create directories
    create_media_dirs
    
    # Setup database
    setup_database
    
    # Create helper scripts
    create_dev_scripts
    
    # Display summary
    display_summary
}

# Run main function
main