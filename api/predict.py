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
    # === KULLANICININ BİLDİRDİĞİ SPESİFİK İSİMLER ===
    "Sport Lisboa e Benfica": "Benfica",
    "SL Benfica": "Benfica",
    "Benfica FC": "Benfica",
    "FC Internazionale Milano": "Inter",
    "FC Internazionale": "Inter",
    "Internazionale Milano": "Inter",
    "Internazionale": "Inter",
    "Inter Milan": "Inter",
    "Inter Milano": "Inter",
    "PAE Olympiakos SFP": "Olympiacos",
    "Olympiakos": "Olympiacos",
    "Olympiacos FC": "Olympiacos",
    "Olympiacos Piraeus": "Olympiacos",
    "Olympiakos Piraeus": "Olympiacos",
    "FK Bodø/Glimt": "Bodø/Glimt",
    "Bodo/Glimt": "Bodø/Glimt",
    "Bodo Glimt": "Bodø/Glimt",
    "FK Bodo/Glimt": "Bodø/Glimt",
    "Galatasaray SK": "Galatasaray",
    "Galatasaray FC": "Galatasaray",
    "Galatasaray AS": "Galatasaray",

    # === TÜRK TAKIMLARI ===
    "Fenerbahce": "Fenerbahçe",
    "Fenerbahce SK": "Fenerbahçe",
    "Fenerbahçe SK": "Fenerbahçe",
    "Besiktas": "Beşiktaş",
    "Besiktas JK": "Beşiktaş",
    "Beşiktaş JK": "Beşiktaş",
    "Trabzonspor AS": "Trabzonspor",

    # === İNGİLİZ TAKIMLARI ===
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
    "Tottenham Hotspur": "Tottenham",
    "Tottenham Hotspur FC": "Tottenham",
    "Spurs": "Tottenham",
    "Arsenal FC": "Arsenal",
    "Chelsea FC": "Chelsea",
    "Liverpool FC": "Liverpool",
    "Newcastle Utd": "Newcastle United",
    "Newcastle": "Newcastle United",
    "Newcastle United FC": "Newcastle United",
    "Aston Villa FC": "Aston Villa",
    "Brighton & Hove Albion": "Brighton",
    "Brighton FC": "Brighton",
    "Wolverhampton Wanderers": "Wolves",
    "Wolverhampton": "Wolves",
    "Wolves FC": "Wolves",
    "Brentford FC": "Brentford",
    "Crystal Palace FC": "Crystal Palace",
    "Bournemouth FC": "Bournemouth",
    "AFC Bournemouth": "Bournemouth",
    "Fulham FC": "Fulham",
    "Everton FC": "Everton",
    "Burnley FC": "Burnley",
    "Sheffield United FC": "Sheffield United",
    "Sheffield Utd": "Sheffield United",

    # === İSPANYOL TAKIMLARI ===
    "Real Madrid CF": "Real Madrid",
    "Real Madrid FC": "Real Madrid",
    "FC Barcelona": "Barcelona",
    "Barca": "Barcelona",
    "Barça": "Barcelona",
    "Atletico Madrid": "Atlético de Madrid",
    "Atletico de Madrid": "Atlético de Madrid",
    "Atlético Madrid": "Atlético de Madrid",
    "Club Atletico de Madrid": "Atlético de Madrid",
    "Atletico": "Atlético de Madrid",
    "Atl. Madrid": "Atlético de Madrid",
    "Atl Madrid": "Atlético de Madrid",
    "Ath Madrid": "Atlético de Madrid",
    "Ath Bilbao": "Athletic Club",
    "Athletic Bilbao": "Athletic Club",
    "Athletic Club Bilbao": "Athletic Club",
    "Athletic Club de Bilbao": "Athletic Club",
    "Villarreal CF": "Villarreal",
    "Villarreal FC": "Villarreal",
    "Real Betis Balompie": "Real Betis",
    "Real Betis Balompié": "Real Betis",
    "Betis": "Real Betis",
    "Real Sociedad": "Sociedad",
    "Real Sociedad de Futbol": "Sociedad",

    # === ALMAN TAKIMLARI ===
    "Bayern Munich": "Bayern München",
    "Bayern Munchen": "Bayern München",
    "Bayern München FC": "Bayern München",
    "FC Bayern München": "Bayern München",
    "FC Bayern Munich": "Bayern München",
    "BVB": "Borussia Dortmund",
    "Dortmund": "Borussia Dortmund",
    "Borussia Dortmund FC": "Borussia Dortmund",
    "Bayer Leverkusen": "Leverkusen",
    "Bayer 04 Leverkusen": "Leverkusen",
    "Leverkusen FC": "Leverkusen",
    "Eintracht Frankfurt": "Frankfurt",
    "E. Frankfurt": "Frankfurt",
    "SGE": "Frankfurt",
    "Eintracht Frankfurt FC": "Frankfurt",

    # === İTALYAN TAKIMLARI ===
    "SSC Napoli": "Napoli",
    "Napoli FC": "Napoli",
    "AC Milan": "Milan",
    "Milan FC": "Milan",
    "Juventus FC": "Juventus",
    "Juve": "Juventus",
    "ACF Fiorentina": "Fiorentina",
    "Fiorentina FC": "Fiorentina",
    "AS Roma": "Roma",
    "Roma FC": "Roma",
    "SS Lazio": "Lazio",
    "Lazio FC": "Lazio",
    "Atalanta BC": "Atalanta",
    "Atalanta Bergamasca Calcio": "Atalanta",
    "US Lecce": "Lecce",
    "Torino FC": "Torino",
    "Bologna FC": "Bologna",
    "Bologna FC 1909": "Bologna",
    "Hellas Verona FC": "Hellas Verona",
    "US Sassuolo": "Sassuolo",
    "Sassuolo Calcio": "Sassuolo",
    "Genoa CFC": "Genoa",
    "Udinese Calcio": "Udinese",
    "UC Sampdoria": "Sampdoria",
    "Empoli FC": "Empoli",
    "US Salernitana 1919": "Salernitana",
    "Cagliari Calcio": "Cagliari",
    "Frosinone Calcio": "Frosinone",

    # === FRANSIZ TAKIMLARI ===
    "PSG": "Paris Saint-Germain",
    "Paris Saint-Germain FC": "Paris Saint-Germain",
    "Paris SG": "Paris Saint-Germain",
    "AS Monaco": "Monaco",
    "AS Monaco FC": "Monaco",
    "Lyon": "Olympique Lyon",
    "Olympique Lyonnais": "Olympique Lyon",
    "OL": "Olympique Lyon",
    "Olympique de Marseille": "Marseille",
    "Marseille FC": "Marseille",
    "OM": "Marseille",
    "Stade Brestois 29": "Brest",

    # === HOLLANDA ===
    "Ajax Amsterdam": "Ajax",
    "AFC Ajax": "Ajax",
    "PSV": "PSV Eindhoven",
    "AZ": "AZ Alkmaar",
    "Feyenoord Rotterdam": "Feyenoord",

    # === BELÇİKA ===
    "Club Bruges": "Club Brugge",
    "Club Brugge KV": "Club Brugge",
    "RSC Union Saint-Gilloise": "Union Saint-Gilloise",
    "Union SG": "Union Saint-Gilloise",
    "Union St. Gilloise": "Union Saint-Gilloise",
    "Royale Union Saint-Gilloise": "Union Saint-Gilloise",
    "R. Union SG": "Union Saint-Gilloise",

    # === PORTEKİZ ===
    "Sporting Lisbon": "Sporting CP",
    "Sporting Lisboa": "Sporting CP",
    "Sporting Clube de Portugal": "Sporting CP",
    "Sporting": "Sporting CP",

    # === DİĞER ===
    "FC Copenhagen": "Copenhagen",
    "FC København": "Copenhagen",
    "Copenhagen FC": "Copenhagen",
    "Slavia Prague": "Slavia Praha",
    "SK Slavia Praha": "Slavia Praha",
    "Slavia Praha FC": "Slavia Praha",
    "Sparta Prague": "Sparta Praha",
    "AC Sparta Praha": "Sparta Praha",
    "Sparta Praha FC": "Sparta Praha",
    "FK Qarabag": "Qarabağ",
    "Qarabag": "Qarabağ",
    "Qarabag FK": "Qarabağ",
    "Qarabağ FK": "Qarabağ",
    "Pafos FC": "Pafos",
    "FC Kairat": "Kairat Almaty",
    "Kairat": "Kairat Almaty",
    "FK Kairat Almaty": "Kairat Almaty",
    "Rangers FC": "Rangers",
    "Glasgow Rangers": "Rangers",
    "Celtic FC": "Celtic",
    "Glasgow Celtic": "Celtic",
    "Crvena Zvezda": "Crvena Zvezda",
    "Red Star Belgrade": "Crvena Zvezda",
    "FK Crvena Zvezda": "Crvena Zvezda",
    "Shakhtar Donetsk FC": "Shakhtar Donetsk",
    "FC Shakhtar Donetsk": "Shakhtar Donetsk",
    "RB Salzburg": "Salzburg",
    "FC Salzburg": "Salzburg",
    "Red Bull Salzburg": "Salzburg",
    "BSC Young Boys": "Young Boys",
    "Young Boys FC": "Young Boys",
    "Union Berlin": "Union Berlin",
    "1. FC Union Berlin": "Union Berlin",
    "RB Leipzig": "Leipzig",
    "RasenBallsport Leipzig": "Leipzig",
    "Slovan Bratislava": "Slovan Bratislava",
    "SK Slovan Bratislava": "Slovan Bratislava",
}

# Baştaki ve sondaki ekler (temizlenecek)
TEAM_PREFIXES = ['FC ', 'FK ', 'AC ', 'AS ', 'SS ', 'US ', 'UC ', 'SC ', 'SK ', 'SL ', 'BC ', 'CF ',
                 'BSC ', 'SSC ', 'AFC ', 'RSC ', 'PAE ', 'ACF ', 'CFC ', 'RB ', 'SFP ']
TEAM_SUFFIXES = [' FC', ' CF', ' AS', ' SK', ' JK', ' KV', ' SC', ' SV', ' FK', ' AC', ' BC',
                 ' SS', ' SSC', ' AFC', ' RSC', ' SFP', ' PAE', ' CFC', ' Calcio', ' de Futbol']


def clean_team_name(name):
    """
    Gelen takım ismini CSV'deki isme eşleştir.
    Agresif temizleme: baş/son ekleri siler, mapping tablosunda arar,
    fuzzy match dener.
    """
    if not name:
        return name

    name = name.strip()

    # 1. Tam eşleşme (mapping tablosu)
    if name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[name]

    # 2. Doğrudan takim_sozlugu'nde var mı?
    if name in takim_sozlugu:
        return name

    # 3. Baştaki ve sondaki ekleri temizle
    cleaned = name
    # Baştaki ekleri temizle
    for prefix in TEAM_PREFIXES:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break
    # Sondaki ekleri temizle
    for suffix in TEAM_SUFFIXES:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()
            break

    # Temizlenmiş hali mapping'de var mı?
    if cleaned in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[cleaned]

    # Temizlenmiş hali takim_sozlugu'nde var mı?
    if cleaned in takim_sozlugu:
        return cleaned

    # 4. Hem baş hem son temizlenmiş halini dene
    double_cleaned = cleaned
    for prefix in TEAM_PREFIXES:
        if double_cleaned.startswith(prefix):
            double_cleaned = double_cleaned[len(prefix):].strip()
            break
    for suffix in TEAM_SUFFIXES:
        if double_cleaned.endswith(suffix):
            double_cleaned = double_cleaned[:-len(suffix)].strip()
            break

    if double_cleaned in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[double_cleaned]
    if double_cleaned in takim_sozlugu:
        return double_cleaned

    # 5. Fuzzy match: CSV'deki takım isimlerinde "contains" araması
    name_lower = name.lower()
    for csv_team in takim_sozlugu:
        csv_lower = csv_team.lower()
        # Gelen isim CSV ismini içeriyor mu veya tam tersi
        if csv_lower in name_lower or name_lower in csv_lower:
            return csv_team

    # 6. Temizlenmiş isimle de fuzzy dene
    cleaned_lower = cleaned.lower()
    for csv_team in takim_sozlugu:
        csv_lower = csv_team.lower()
        if csv_lower in cleaned_lower or cleaned_lower in csv_lower:
            return csv_team

    # Hiçbiri yoksa orijinal ismi dön
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
