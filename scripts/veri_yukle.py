"""
Veri yükleme scripti.
Maç verilerini data/tum_maclar.csv dosyasına yazar.
Yeni maç verileri eklemek için bu dosyayı düzenleyebilirsiniz.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Veri dosyasının yolunu belirle
output_path = os.path.join(DATA_DIR, 'tum_maclar.csv')

print(f"📂 Veri dosyası konumu: {output_path}")
print("ℹ️  Yeni maç verisi eklemek için data/tum_maclar.csv dosyasını düzenleyin.")
print("ℹ️  Format: tarih,ev_sahibi,deplasman,ev_gol,dep_gol")
print("ℹ️  Örnek: 2024-01-15,Barcelona,Real Madrid,2,1")
