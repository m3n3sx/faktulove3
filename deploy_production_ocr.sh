#!/bin/bash
# FaktuLove Production OCR Deployment Script

set -e

echo "🚀 Deploying FaktuLove Production OCR"
echo "===================================="

# Copy files to server
echo "📁 Copying files to server..."
scp -i /home/ooxo/.ssh/klucz1.pem install_production_ocr.sh admin@ec2-13-60-160-136.eu-north-1.compute.amazonaws.com:/home/admin/
scp -i /home/ooxo/.ssh/klucz1.pem production_ocr_service.py admin@ec2-13-60-160-136.eu-north-1.compute.amazonaws.com:/home/admin/faktulove/
scp -i /home/ooxo/.ssh/klucz1.pem create_admin.py admin@ec2-13-60-160-136.eu-north-1.compute.amazonaws.com:/home/admin/faktulove/
scp -i /home/ooxo/.ssh/klucz1.pem faktulove-ocr.service admin@ec2-13-60-160-136.eu-north-1.compute.amazonaws.com:/home/admin/

echo "✅ Files copied to server"

# Connect to server and run installation
echo "🔧 Running installation on server..."
ssh -i /home/ooxo/.ssh/klucz1.pem admin@ec2-13-60-160-136.eu-north-1.compute.amazonaws.com << 'EOF'

# Install OCR engines
echo "📖 Installing OCR engines..."
chmod +x /home/admin/install_production_ocr.sh
/home/admin/install_production_ocr.sh

# Setup admin user
echo "👤 Setting up admin user..."
cd /home/admin/faktulove
python3 create_admin.py

# Install systemd service
echo "⚙️ Installing systemd service..."
sudo cp /home/admin/faktulove-ocr.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable faktulove-ocr
sudo systemctl start faktulove-ocr

# Check service status
echo "📊 Checking service status..."
sudo systemctl status faktulove-ocr --no-pager

# Test OCR service
echo "🧪 Testing OCR service..."
sleep 5
curl -s http://localhost:8001/health | python3 -m json.tool

echo "✅ Production OCR deployment completed!"
echo "🌐 Access admin at: https://faktulove.ooxo.pl/admin/"
echo "👤 Username: ooxo"
echo "🔑 Password: ooxo"

EOF

echo "🎉 Deployment completed successfully!"
