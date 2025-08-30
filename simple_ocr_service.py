#!/usr/bin/env python3
"""
Simple OCR Service for FaktuLove Production
"""

import json
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleOCRHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = self.path
        
        if path == '/health':
            self.send_json_response({
                'status': 'healthy',
                'service': 'Simple OCR Service',
                'version': '1.0.0',
                'timestamp': time.time()
            })
            
        elif path == '/status':
            self.send_json_response({
                'service': 'Simple OCR Service',
                'status': 'running',
                'engines': ['tesseract'],
                'supported_formats': ['pdf', 'jpg', 'jpeg', 'png'],
                'languages': ['pol', 'eng']
            })
            
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests"""
        path = self.path
        
        if path == '/ocr/process':
            self.send_json_response({
                'status': 'success',
                'text': 'OCR processing completed (mock response)',
                'confidence': 0.95,
                'processing_time': 1.5,
                'engine': 'tesseract',
                'timestamp': time.time()
            })
        else:
            self.send_error(404, "Endpoint not found")
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to use proper logging"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """Main function"""
    server_address = ('0.0.0.0', 8001)
    httpd = HTTPServer(server_address, SimpleOCRHandler)
    
    logger.info("🚀 Simple OCR Service starting...")
    logger.info(f"🌐 Server running on http://0.0.0.0:8001")
    logger.info(f"🏥 Health check: http://localhost:8001/health")
    logger.info("⏹️ Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down OCR service...")
        httpd.shutdown()
        logger.info("✅ OCR service stopped")

if __name__ == '__main__':
    main()