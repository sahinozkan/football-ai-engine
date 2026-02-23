"""
Sağlık Kontrolü API Endpoint (GET /api/health)
Vercel Serverless Function olarak çalışır.
"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            'status': 'ok',
            'service': 'Football AI Engine',
            'message': 'AI Engine calisiyor!'
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
