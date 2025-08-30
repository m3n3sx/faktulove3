#!/usr/bin/env python3
"""Mock OCR Service na porcie 8001"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockOCRHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'service': 'Mock OCR Service',
                'timestamp': time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    server = HTTPServer(('localhost', 8001), MockOCRHandler)
    print("🚀 Mock OCR Service running on http://localhost:8001")
    print("📡 Health check: http://localhost:8001/health")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping mock service...")
        server.shutdown()

if __name__ == '__main__':
    main()
