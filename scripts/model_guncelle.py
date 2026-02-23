"""
Model güncelleme scripti.
Veri dosyasından modelleri yeniden eğitir ve models/ klasörüne kaydeder.
"""
import os
import sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib

# Proje kök dizinini bul
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# 1. Güncel Veriyi Oku
print("📂 Veriler okunuyor...")
try:
    df = pd.read_csv(os.path.join(DATA_DIR, 'tum_maclar.csv'))
    print(f"✅ Toplam {len(df)} satır veri okundu.")
except Exception as e:
    print(f"❌ HATA: Veri dosyası okunamadı! {e}")
    sys.exit(1)

# Tarihi datetime formatına çevirelim
df['tarih'] = pd.to_datetime(df['tarih'])

# 2. Veriyi Hazırla
tum_takimlar = pd.concat([df['ev_sahibi'], df['deplasman']]).unique()
takim_sozlugu = {takim: i for i, takim in enumerate(tum_takimlar)}

df['ev_kodu'] = df['ev_sahibi'].map(takim_sozlugu)
df['dep_kodu'] = df['deplasman'].map(takim_sozlugu)

# Basit özellikler
X = df[['ev_kodu', 'dep_kodu', 'ev_gol', 'dep_gol']].values

# Etiketler
# Kazanan: 2 = Ev, 1 = Beraberlik, 0 = Deplasman
y_kazanan = []
for _, row in df.iterrows():
    if row['ev_gol'] > row['dep_gol']:
        y_kazanan.append(2)
    elif row['ev_gol'] < row['dep_gol']:
        y_kazanan.append(0)
    else:
        y_kazanan.append(1)

y_ev_gol = df['ev_gol'].values
y_dep_gol = df['dep_gol'].values

# 3. Modelleri Eğit
print("🧠 Modeller yeniden eğitiliyor...")

model_kazanan = RandomForestClassifier(n_estimators=100, random_state=42)
model_kazanan.fit(X, y_kazanan)
print("  ✅ Kazanan tahmin modeli eğitildi.")

model_ev_gol = RandomForestRegressor(n_estimators=100, random_state=42)
model_ev_gol.fit(X, y_ev_gol)
print("  ✅ Ev gol modeli eğitildi.")

model_dep_gol = RandomForestRegressor(n_estimators=100, random_state=42)
model_dep_gol.fit(X, y_dep_gol)
print("  ✅ Deplasman gol modeli eğitildi.")

# 4. Modelleri Kaydet
joblib.dump(model_kazanan, os.path.join(MODELS_DIR, 'futbol_kahini.pkl'))
joblib.dump(model_ev_gol, os.path.join(MODELS_DIR, 'ev_gol_modeli.pkl'))
joblib.dump(model_dep_gol, os.path.join(MODELS_DIR, 'dep_gol_modeli.pkl'))

print(f"\n🎉 Tüm modeller '{MODELS_DIR}' klasörüne kaydedildi!")
print(f"📊 Toplam {len(tum_takimlar)} takım, {len(df)} maç verisiyle eğitildi.")
