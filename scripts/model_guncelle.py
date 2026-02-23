"""
Model güncelleme scripti.
Veri dosyasından modelleri yeniden eğitir ve models/ klasörüne kaydeder.

Feature sırası (6 özellik):
  [ev_kodu, dep_kodu, ev_gol_ort, ev_yedigi_ort, dep_gol_ort, dep_yedigi_ort]

  - ev_kodu / dep_kodu: Takımın sayısal kodu
  - ev_gol_ort: Ev sahibi takımın son 3 maçtaki ortalama attığı gol
  - ev_yedigi_ort: Ev sahibi takımın son 3 maçtaki ortalama yediği gol
  - dep_gol_ort: Deplasman takımının son 3 maçtaki ortalama attığı gol
  - dep_yedigi_ort: Deplasman takımının son 3 maçtaki ortalama yediği gol
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib

# Proje kök dizinini bul
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# 1. Güncel Veriyi Oku
print("[*] Veriler okunuyor...")
try:
    df = pd.read_csv(os.path.join(DATA_DIR, 'tum_maclar.csv'))
    print(f"[OK] Toplam {len(df)} satir veri okundu.")
except Exception as e:
    print(f"[HATA] Veri dosyasi okunamadi! {e}")
    sys.exit(1)

# Tarihi datetime formatına çevirelim ve sıralayalım
df['tarih'] = pd.to_datetime(df['tarih'])
df = df.sort_values('tarih').reset_index(drop=True)

# 2. Takım Kodlarını Oluştur
tum_takimlar = pd.concat([df['ev_sahibi'], df['deplasman']]).unique()
takim_sozlugu = {takim: i for i, takim in enumerate(tum_takimlar)}

df['ev_kodu'] = df['ev_sahibi'].map(takim_sozlugu)
df['dep_kodu'] = df['deplasman'].map(takim_sozlugu)

# 3. Her Maç İçin Son 3 Maç Rolling İstatistiklerini Hesapla
print("[*] Rolling istatistikler hesaplaniyor (son 3 mac)...")

ev_gol_ort_list = []
ev_yedigi_ort_list = []
dep_gol_ort_list = []
dep_yedigi_ort_list = []

for idx in range(len(df)):
    row = df.iloc[idx]
    ev_takim = row['ev_sahibi']
    dep_takim = row['deplasman']
    
    # Bu maçtan önceki tüm maçlar (iloc position-based)
    onceki_maclar = df.iloc[:idx] if idx > 0 else pd.DataFrame(columns=df.columns)
    
    # --- Ev sahibi takımın son 3 maçı ---
    ev_maclari = onceki_maclar[
        (onceki_maclar['ev_sahibi'] == ev_takim) | (onceki_maclar['deplasman'] == ev_takim)
    ].tail(3)
    
    if len(ev_maclari) >= 3:
        ev_goller = []
        ev_yedigi = []
        for _, m in ev_maclari.iterrows():
            if m['ev_sahibi'] == ev_takim:
                ev_goller.append(m['ev_gol'])
                ev_yedigi.append(m['dep_gol'])
            else:
                ev_goller.append(m['dep_gol'])
                ev_yedigi.append(m['ev_gol'])
        ev_gol_ort_list.append(sum(ev_goller) / 3)
        ev_yedigi_ort_list.append(sum(ev_yedigi) / 3)
    else:
        ev_gol_ort_list.append(0)
        ev_yedigi_ort_list.append(0)
    
    # --- Deplasman takımının son 3 maçı ---
    dep_maclari = onceki_maclar[
        (onceki_maclar['ev_sahibi'] == dep_takim) | (onceki_maclar['deplasman'] == dep_takim)
    ].tail(3)
    
    if len(dep_maclari) >= 3:
        dep_goller = []
        dep_yedigi_g = []
        for _, m in dep_maclari.iterrows():
            if m['ev_sahibi'] == dep_takim:
                dep_goller.append(m['ev_gol'])
                dep_yedigi_g.append(m['dep_gol'])
            else:
                dep_goller.append(m['dep_gol'])
                dep_yedigi_g.append(m['ev_gol'])
        dep_gol_ort_list.append(sum(dep_goller) / 3)
        dep_yedigi_ort_list.append(sum(dep_yedigi_g) / 3)
    else:
        dep_gol_ort_list.append(0)
        dep_yedigi_ort_list.append(0)

df['ev_gol_ort'] = ev_gol_ort_list
df['ev_yedigi_ort'] = ev_yedigi_ort_list
df['dep_gol_ort'] = dep_gol_ort_list
df['dep_yedigi_ort'] = dep_yedigi_ort_list

# 4. Feature ve Label Hazırla (6 özellik)
X = df[['ev_kodu', 'dep_kodu', 'ev_gol_ort', 'ev_yedigi_ort', 'dep_gol_ort', 'dep_yedigi_ort']].values

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

print(f"   Feature boyutu: {X.shape} (satir x ozellik)")

# 5. Modelleri Eğit
print("[*] Modeller yeniden egitiliyor (6 feature)...")

model_kazanan = RandomForestClassifier(n_estimators=100, random_state=42)
model_kazanan.fit(X, y_kazanan)
print("  [OK] Kazanan tahmin modeli egitildi.")

model_ev_gol = RandomForestRegressor(n_estimators=100, random_state=42)
model_ev_gol.fit(X, y_ev_gol)
print("  [OK] Ev gol modeli egitildi.")

model_dep_gol = RandomForestRegressor(n_estimators=100, random_state=42)
model_dep_gol.fit(X, y_dep_gol)
print("  [OK] Deplasman gol modeli egitildi.")

# 6. Modelleri Kaydet
joblib.dump(model_kazanan, os.path.join(MODELS_DIR, 'futbol_kahini.pkl'))
joblib.dump(model_ev_gol, os.path.join(MODELS_DIR, 'ev_gol_modeli.pkl'))
joblib.dump(model_dep_gol, os.path.join(MODELS_DIR, 'dep_gol_modeli.pkl'))

print(f"\n[TAMAM] Tum modeller '{MODELS_DIR}' klasorune kaydedildi!")
print(f"[INFO] Toplam {len(tum_takimlar)} takim, {len(df)} mac verisiyle egitildi.")
print(f"[INFO] Model feature sayisi: 6 [ev_kodu, dep_kodu, ev_gol_ort, ev_yedigi_ort, dep_gol_ort, dep_yedigi_ort]")
