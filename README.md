# ⚽ Football AI Engine

Bağımsız Futbol Maç Tahmin Motoru. Vercel Serverless Functions üzerinde çalışır.

## 📁 Proje Yapısı

```
football-ai-engine/
├── api/                    # Vercel Serverless Functions
│   ├── health.py           # GET  /api/health  → Sağlık kontrolü
│   ├── predict.py          # POST /api/predict → Maç tahmini
│   └── teams.py            # GET  /api/teams   → Takım listesi
├── models/                 # Eğitilmiş ML Modelleri
│   ├── futbol_kahini.pkl   # Kazanan tahmin modeli
│   ├── ev_gol_modeli.pkl   # Ev sahibi gol tahmin modeli
│   └── dep_gol_modeli.pkl  # Deplasman gol tahmin modeli
├── data/                   # Veri dosyaları
│   └── tum_maclar.csv      # Maç verileri
├── scripts/                # Yardımcı scriptler
│   ├── model_guncelle.py   # Model eğitim scripti
│   └── veri_yukle.py       # Veri yükleme scripti
├── requirements.txt        # Python bağımlılıkları
├── vercel.json             # Vercel yapılandırması
├── .gitignore
└── README.md
```

## 🚀 API Endpoints

### `GET /api/health`
Sağlık kontrolü endpoint'i.

**Response:**
```json
{
    "status": "ok",
    "service": "Football AI Engine",
    "message": "AI Engine calisiyor!"
}
```

### `GET /api/teams`
Sistemdeki tüm takımların listesini döndürür.

**Response:**
```json
{
    "teams": ["Arsenal", "Barcelona", "Real Madrid", ...],
    "count": 85
}
```

### `POST /api/predict`
İki takım arasındaki maç sonucunu tahmin eder.

**Request Body:**
```json
{
    "home_team": "Barcelona",
    "away_team": "Real Madrid"
}
```

**Response:**
```json
{
    "prediction": "Ev Sahibi",
    "score_home": 2,
    "score_away": 1,
    "confidence": "%67.3",
    "message": "Model, Barcelona'in 2, Real Madrid'in 1 gol atacağını öngörüyor."
}
```

## 🔧 Kurulum (Lokal Geliştirme)

```bash
# 1. Repoyu klonla
git clone https://github.com/KULLANICI_ADINIZ/football-ai-engine.git
cd football-ai-engine

# 2. Virtual environment oluştur
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Bağımlılıkları yükle
pip install -r requirements.txt
```

## 🌐 Vercel'e Deploy

1. GitHub'a push et
2. [Vercel](https://vercel.com) → "New Project"
3. GitHub reposunu seç: `football-ai-engine`
4. Framework Preset: **Other**
5. Deploy et!

## 🔗 Ana Projeyle Entegrasyon

Ana proje (football-predictor) bu AI Engine'i ayrı bir servis olarak kullanır.

Frontend'de API URL'ini Vercel URL'ine yönlendirin:

```javascript
// Örnek: Ana projedeki frontend kodu
const AI_API_URL = 'https://football-ai-engine.vercel.app';

// Takım listesini çek
fetch(`${AI_API_URL}/api/teams`)

// Tahmin yap
fetch(`${AI_API_URL}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ home_team: 'Barcelona', away_team: 'Real Madrid' })
})
```

## 📊 Teknolojiler

- **Python 3.9+**
- **scikit-learn** — Makine öğrenimi modelleri
- **pandas** — Veri işleme
- **joblib** — Model serileştirme
- **Vercel Serverless Functions** — Deployment
