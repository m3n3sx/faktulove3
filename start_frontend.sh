#!/bin/bash

# FaktuLove OCR - Frontend Development Server
# This script starts the React development server

set -e

echo "🚀 Starting FaktuLove OCR Frontend Development Server"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed. Please install Node.js 16+ to continue."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    print_warning "Node.js version 16+ is required. Current version: $(node -v)"
    exit 1
fi

print_success "Node.js version: $(node -v)"

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    print_warning "Frontend directory not found. Creating React app..."
    npx create-react-app frontend --template typescript
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
    print_success "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Check if Django backend is running
print_status "Checking Django backend..."
if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
    print_success "Django backend is running on http://localhost:8000"
else
    print_warning "Django backend is not running on http://localhost:8000"
    print_warning "Please start the Django server first: python manage.py runserver"
    print_warning "Frontend will use mock data until backend is available"
fi

# Start development server
print_status "Starting React development server..."
print_status "Frontend will be available at: http://localhost:3000"
print_status "API proxy configured to: http://localhost:8000"
echo ""

# Start the development server
npm start
