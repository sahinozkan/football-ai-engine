"""
Takım Listesi API Endpoint (GET /api/teams)
Vercel Serverless Function olarak çalışır.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import joblib
import pandas as pd

# --- Model Yükleme ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

MODELS_LOADED = False
LOAD_ERROR = ""
takim_sozlugu = {}

try:
    df = pd.read_csv(os.path.join(DATA_DIR, 'tum_maclar.csv'))
    df["tarih"] = pd.to_datetime(df["tarih"])
    df = df.sort_values("tarih")
    tum_takimlar = pd.concat([df['ev_sahibi'], df['deplasman']]).unique()
    takim_sozlugu = {takim: i for i, takim in enumerate(tum_takimlar)}
    MODELS_LOADED = True
except Exception as e:
    MODELS_LOADED = False
    LOAD_ERROR = str(e)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if MODELS_LOADED else 500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if not MODELS_LOADED:
            self.wfile.write(json.dumps({'error': f'Model hatası: {LOAD_ERROR}'}).encode('utf-8'))
            return

        response = {
            'teams': sorted(list(takim_sozlugu.keys())),
            'count': len(takim_sozlugu)
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
