"""
Maç Tahmin API Endpoint (POST /api/predict)
Vercel Serverless Function olarak çalışır.

Feature sırası (6 özellik - model_guncelle.py ile aynı):
  [ev_kodu, dep_kodu, ev_gol_ort, ev_yedigi_ort, dep_gol_ort, dep_yedigi_ort]
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import joblib
import pandas as pd
import numpy as np

# --- Takım İsmi Eşleştirme ---
# Gelen isim -> CSV'deki isim
TEAM_NAME_MAP = {
    # Genel kısaltmalar ve alternatif isimler
    "PSG": "Paris Saint-Germain",
    "Paris Saint-Germain FC": "Paris Saint-Germain",
    "Bayern Munich": "Bayern München",
    "Bayern Munchen": "Bayern München",
    "Bayern München FC": "Bayern München",
    "Atletico Madrid": "Atlético de Madrid",
    "Atletico de Madrid": "Atlético de Madrid",
    "Atletico": "Atlético de Madrid",
    "Atl. Madrid": "Atlético de Madrid",
    "Atl Madrid": "Atlético de Madrid",
    "Ath Madrid": "Atlético de Madrid",
    "BVB": "Borussia Dortmund",
    "Dortmund": "Borussia Dortmund",
    "Borussia Dortmund FC": "Borussia Dortmund",
    "Man City": "Manchester City",
    "Manchester City FC": "Manchester City",
    "Man United": "Man United",
    "Manchester United": "Man United",
    "Manchester United FC": "Man United",
    "Nott'm Forest": "Nottingham Forest",
    "Nottingham Forest FC": "Nottingham Forest",
    "Nott Forest": "Nottingham Forest",
    "West Ham": "West Ham United",
    "West Ham United FC": "West Ham United",
    "Fenerbahce": "Fenerbahçe",
    "Fenerbahce SK": "Fenerbahçe",
    "Fenerbahçe SK": "Fenerbahçe",
    "Galatasaray SK": "Galatasaray",
    "Galatasaray FC": "Galatasaray",
    "Besiktas": "Beşiktaş",
    "Besiktas JK": "Beşiktaş",
    "Beşiktaş JK": "Beşiktaş",
    "Trabzonspor AS": "Trabzonspor",
    "Real Betis Balompie": "Real Betis",
    "Real Betis Balompié": "Real Betis",
    "Betis": "Real Betis",
    "Lyon": "Olympique Lyon",
    "Olympique Lyonnais": "Olympique Lyon",
    "OL": "Olympique Lyon",
    "Rangers FC": "Rangers",
    "Fiorentina FC": "Fiorentina",
    "ACF Fiorentina": "Fiorentina",
    "AZ": "AZ Alkmaar",
    "Sporting Lisbon": "Sporting CP",
    "Sporting Lisboa": "Sporting CP",
    "Sporting": "Sporting CP",
    "Club Bruges": "Club Brugge",
    "Club Brugge KV": "Club Brugge",
    "Bayer Leverkusen": "Leverkusen",
    "Leverkusen FC": "Leverkusen",
    "Eintracht Frankfurt": "Frankfurt",
    "E. Frankfurt": "Frankfurt",
    "SGE": "Frankfurt",
    "Tottenham Hotspur": "Tottenham",
    "Spurs": "Tottenham",
    "Tottenham Hotspur FC": "Tottenham",
    "FC Barcelona": "Barcelona",
    "Barca": "Barcelona",
    "Barça": "Barcelona",
    "Real Madrid CF": "Real Madrid",
    "Real Madrid FC": "Real Madrid",
    "Inter Milan": "Inter",
    "FC Internazionale": "Inter",
    "Internazionale": "Inter",
    "Inter Milano": "Inter",
    "SSC Napoli": "Napoli",
    "Napoli FC": "Napoli",
    "AC Milan": "Milan",
    "Milan FC": "Milan",
    "Juventus FC": "Juventus",
    "Juve": "Juventus",
    "AS Monaco": "Monaco",
    "AS Monaco FC": "Monaco",
    "Newcastle Utd": "Newcastle United",
    "Newcastle": "Newcastle United",
    "Arsenal FC": "Arsenal",
    "Chelsea FC": "Chelsea",
    "Liverpool FC": "Liverpool",
    "Ajax Amsterdam": "Ajax",
    "AFC Ajax": "Ajax",
    "SL Benfica": "Benfica",
    "Benfica FC": "Benfica",
    "Olympiakos": "Olympiacos",
    "Olympiacos FC": "Olympiacos",
    "Olympiacos Piraeus": "Olympiacos",
    "Ath Bilbao": "Athletic Club",
    "Athletic Bilbao": "Athletic Club",
    "Athletic Club Bilbao": "Athletic Club",
    "Villarreal CF": "Villarreal",
    "Villarreal FC": "Villarreal",
    "Copenhagen FC": "Copenhagen",
    "FC Copenhagen": "Copenhagen",
    "FC København": "Copenhagen",
    "Slavia Prague": "Slavia Praha",
    "SK Slavia Praha": "Slavia Praha",
    "Sparta Prague": "Sparta Praha",
    "AC Sparta Praha": "Sparta Praha",
    "Bodo/Glimt": "Bodø/Glimt",
    "FK Bodø/Glimt": "Bodø/Glimt",
    "Bodo Glimt": "Bodø/Glimt",
    "RSC Union Saint-Gilloise": "Union Saint-Gilloise",
    "Union SG": "Union Saint-Gilloise",
    "Union St. Gilloise": "Union Saint-Gilloise",
    "FK Qarabag": "Qarabağ",
    "Qarabag": "Qarabağ",
    "Qarabag FK": "Qarabağ",
    "Pafos FC": "Pafos",
    "FC Kairat": "Kairat Almaty",
    "Kairat": "Kairat Almaty",
    "FK Kairat Almaty": "Kairat Almaty",
}

# Takım isimlerinden temizlenecek ekler (sırasıyla)
TEAM_SUFFIXES = [' FC', ' CF', ' AS', ' SK', ' JK', ' KV', ' SC', ' SV', ' FK', ' AC', ' SS', ' SSC', ' AFC', ' RSC']


def clean_team_name(name):
    """
    Gelen takım ismini CSV'deki isme eşleştir.
    1. Önce tam eşleşme dene (mapping table)
    2. Sonra ekleri temizleyerek dene
    3. Bulunamazsa orijinal ismi dön
    """
    if not name:
        return name

    # 1. Tam eşleşme (mapping tablosu)
    if name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[name]

    # 2. Sondaki FC, CF, AS vb. ekleri temizle ve mapping'de ara
    cleaned = name.strip()
    for suffix in TEAM_SUFFIXES:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()
            break

    # Temizlenmiş hali mapping'de var mı?
    if cleaned in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[cleaned]

    # 3. Temizlenmiş hali doğrudan takim_sozlugu'nde var mı?
    if cleaned in takim_sozlugu:
        return cleaned

    # 4. Hiçbiri yoksa orijinal ismi dön
    return name


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
    """Takımın son 3 maç istatistiklerini hesapla (ort gol, ort yediği)"""
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
    def _send_cors_headers(self):
        """Tüm response'lara CORS header ekle"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_POST(self):
        if not MODELS_LOADED:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Model hatası: {LOAD_ERROR}'}).encode('utf-8'))
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            ev_raw = data.get('home_team', '')
            dep_raw = data.get('away_team', '')

            # Takım isimlerini temizle/eşleştir
            ev = clean_team_name(ev_raw)
            dep = clean_team_name(dep_raw)

            if ev not in takim_sozlugu or dep not in takim_sozlugu:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                error_msg = f"Takım veritabanında bulunamadı."
                if ev not in takim_sozlugu:
                    error_msg += f" '{ev_raw}' (temizlenmiş: '{ev}') bulunamadı."
                if dep not in takim_sozlugu:
                    error_msg += f" '{dep_raw}' (temizlenmiş: '{dep}') bulunamadı."
                self.wfile.write(json.dumps({
                    'error': error_msg
                }, ensure_ascii=False).encode('utf-8'))
                return

            ev_kodu = takim_sozlugu[ev]
            dep_kodu = takim_sozlugu[dep]
            ev_gol, ev_yedigi = get_team_stats(ev)
            dep_gol, dep_yedigi = get_team_stats(dep)

            # 6 feature: model_guncelle.py ile aynı sırada
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
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
