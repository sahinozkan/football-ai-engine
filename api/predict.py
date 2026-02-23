"""
Maç Tahmin API Endpoint (POST /api/predict)
Vercel Serverless Function olarak çalışır.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import joblib
import pandas as pd
import numpy as np

# --- Model Yükleme ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

MODELS_LOADED = False
LOAD_ERROR = ""
model_kazanan = None
model_ev_gol = None
model_dep_gol = None
df = None
takim_sozlugu = {}

try:
    model_kazanan = joblib.load(os.path.join(MODELS_DIR, 'futbol_kahini.pkl'))
    model_ev_gol = joblib.load(os.path.join(MODELS_DIR, 'ev_gol_modeli.pkl'))
    model_dep_gol = joblib.load(os.path.join(MODELS_DIR, 'dep_gol_modeli.pkl'))
    df = pd.read_csv(os.path.join(DATA_DIR, 'tum_maclar.csv'))

    df["tarih"] = pd.to_datetime(df["tarih"])
    df = df.sort_values("tarih")

    tum_takimlar = pd.concat([df['ev_sahibi'], df['deplasman']]).unique()
    takim_sozlugu = {takim: i for i, takim in enumerate(tum_takimlar)}
    MODELS_LOADED = True
except Exception as e:
    MODELS_LOADED = False
    LOAD_ERROR = str(e)


def get_team_stats(team_name):
    """Takımın son 3 maç istatistiklerini hesapla"""
    takim_maclari = df[(df["ev_sahibi"] == team_name) | (df["deplasman"] == team_name)].tail(3)
    if len(takim_maclari) < 3:
        return 0, 0

    goller, yedigi = [], []
    for _, row in takim_maclari.iterrows():
        if row["ev_sahibi"] == team_name:
            goller.append(row["ev_gol"])
            yedigi.append(row["dep_gol"])
        else:
            goller.append(row["dep_gol"])
            yedigi.append(row["ev_gol"])
    return sum(goller) / 3, sum(yedigi) / 3


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_header('Access-Control-Allow-Origin', '*')

        if not MODELS_LOADED:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Model hatası: {LOAD_ERROR}'}).encode('utf-8'))
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            ev = data.get('home_team')
            dep = data.get('away_team')

            if ev not in takim_sozlugu or dep not in takim_sozlugu:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Takım veritabanında bulunamadı.'
                }, ensure_ascii=False).encode('utf-8'))
                return

            ev_kodu = takim_sozlugu[ev]
            dep_kodu = takim_sozlugu[dep]
            ev_gol, ev_yedigi = get_team_stats(ev)
            dep_gol, dep_yedigi = get_team_stats(dep)

            girdi = [[ev_kodu, dep_kodu, ev_gol, ev_yedigi, dep_gol, dep_yedigi]]

            sonuc_kodu = model_kazanan.predict(girdi)[0]
            olasiliklar = model_kazanan.predict_proba(girdi)[0]
            guven = max(olasiliklar) * 100

            tahmin_ev_gol = int(round(model_ev_gol.predict(girdi)[0]))
            tahmin_dep_gol = int(round(model_dep_gol.predict(girdi)[0]))

            if sonuc_kodu == 2:
                kazanan = "Ev Sahibi"
            elif sonuc_kodu == 0:
                kazanan = "Deplasman"
            else:
                kazanan = "Beraberlik"

            response = {
                'prediction': kazanan,
                'score_home': tahmin_ev_gol,
                'score_away': tahmin_dep_gol,
                'confidence': f"%{guven:.1f}",
                'message': f"Model, {ev}'in {tahmin_ev_gol}, {dep}'in {tahmin_dep_gol} gol atacağını öngörüyor."
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
