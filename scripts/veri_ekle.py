"""
Yeni maç verilerini tum_maclar.csv'ye ekleyen script.
JSON'daki takım isimlerini CSV'deki mevcut isimlere eşleştirir.
Zaten var olan maçları tekrar eklemez (duplikasyon kontrolü).
"""
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CSV_PATH = os.path.join(DATA_DIR, 'tum_maclar.csv')

# --- İsim Eşleştirme Sözlüğü ---
# JSON'daki isim -> CSV'deki isim
TEAM_NAME_MAP = {
    # CL JSON'daki isimler
    "Paris Saint-Germain": "Paris Saint-Germain",
    "Bayern München": "Bayern München",
    "Atlético de Madrid": "Atlético de Madrid",
    "Borussia Dortmund": "Borussia Dortmund",
    "PSV Eindhoven": "PSV Eindhoven",
    "Union Saint-Gilloise": "Union Saint-Gilloise",
    "Slavia Praha": "Slavia Praha",
    "Bodø/Glimt": "Bodø/Glimt",
    "Kairat Almaty": "Kairat Almaty",
    "Club Brugge": "Club Brugge",
    "Newcastle United": "Newcastle United",
    "Manchester City": "Manchester City",
    "Athletic Club": "Athletic Club",
    "Sporting CP": "Sporting CP",
    "Eintracht Frankfurt": "Frankfurt",
    "Frankfurt": "Frankfurt",
    # Europa League JSON'daki isimler
    "Fenerbahce": "Fenerbahçe",
    "Sparta Praha": "Sparta Praha",
    "Real Betis": "Real Betis",
    "Olympique Lyon": "Olympique Lyon",
    "West Ham United": "West Ham United",
    "Nottingham Forest": "Nottingham Forest",
    "Rangers": "Rangers",
    "Fiorentina": "Fiorentina",
    "AZ Alkmaar": "AZ Alkmaar",
}

def map_team_name(name):
    """Takım ismini CSV formatına eşleştir"""
    return TEAM_NAME_MAP.get(name, name)

# --- Mevcut CSV'yi oku ---
print("📂 Mevcut CSV okunuyor...")
df_existing = pd.read_csv(CSV_PATH)
print(f"   Mevcut satır sayısı: {len(df_existing)}")

# Mevcut takımları listele
existing_teams = set(pd.concat([df_existing['ev_sahibi'], df_existing['deplasman']]).unique())
print(f"   Mevcut takım sayısı: {len(existing_teams)}")

# --- Yeni Maç Verileri ---
# Champions League 2025-26
cl_matches = [
    # Matchday 1 - Sep 16
    {"date":"2025-09-16","home":"Athletic Club","away":"Arsenal","hg":0,"ag":2},
    {"date":"2025-09-16","home":"PSV Eindhoven","away":"Union Saint-Gilloise","hg":1,"ag":3},
    {"date":"2025-09-16","home":"Juventus","away":"Borussia Dortmund","hg":4,"ag":4},
    {"date":"2025-09-16","home":"Real Madrid","away":"Marseille","hg":2,"ag":1},
    {"date":"2025-09-16","home":"Benfica","away":"Qarabağ","hg":2,"ag":3},
    {"date":"2025-09-16","home":"Tottenham","away":"Villarreal","hg":1,"ag":0},
    # Matchday 1 - Sep 17
    {"date":"2025-09-17","home":"Olympiacos","away":"Pafos","hg":0,"ag":0},
    {"date":"2025-09-17","home":"Slavia Praha","away":"Bodø/Glimt","hg":2,"ag":2},
    {"date":"2025-09-17","home":"Ajax","away":"Inter","hg":0,"ag":2},
    {"date":"2025-09-17","home":"Bayern München","away":"Chelsea","hg":3,"ag":1},
    {"date":"2025-09-17","home":"Liverpool","away":"Atlético de Madrid","hg":3,"ag":2},
    {"date":"2025-09-17","home":"Paris Saint-Germain","away":"Atalanta","hg":4,"ag":0},
    # Matchday 2 - Sep 30
    {"date":"2025-09-30","home":"Atalanta","away":"Club Brugge","hg":2,"ag":1},
    {"date":"2025-09-30","home":"Kairat Almaty","away":"Real Madrid","hg":0,"ag":5},
    {"date":"2025-09-30","home":"Atlético de Madrid","away":"Frankfurt","hg":5,"ag":1},
    {"date":"2025-09-30","home":"Chelsea","away":"Benfica","hg":1,"ag":0},
    {"date":"2025-09-30","home":"Inter","away":"Slavia Praha","hg":3,"ag":0},
    {"date":"2025-09-30","home":"Bodø/Glimt","away":"Tottenham","hg":2,"ag":2},
    {"date":"2025-09-30","home":"Galatasaray","away":"Liverpool","hg":1,"ag":0},
    {"date":"2025-09-30","home":"Marseille","away":"Ajax","hg":4,"ag":0},
    {"date":"2025-09-30","home":"Pafos","away":"Bayern München","hg":1,"ag":5},
    # Matchday 2 - Oct 1
    {"date":"2025-10-01","home":"Qarabağ","away":"Copenhagen","hg":2,"ag":0},
    {"date":"2025-10-01","home":"Union Saint-Gilloise","away":"Newcastle United","hg":0,"ag":4},
    {"date":"2025-10-01","home":"Arsenal","away":"Olympiacos","hg":2,"ag":0},
    {"date":"2025-10-01","home":"Monaco","away":"Manchester City","hg":2,"ag":2},
    {"date":"2025-10-01","home":"Leverkusen","away":"PSV Eindhoven","hg":1,"ag":1},
    {"date":"2025-10-01","home":"Borussia Dortmund","away":"Athletic Club","hg":4,"ag":1},
    {"date":"2025-10-01","home":"Barcelona","away":"Paris Saint-Germain","hg":1,"ag":2},
    {"date":"2025-10-01","home":"Napoli","away":"Sporting CP","hg":2,"ag":1},
    {"date":"2025-10-01","home":"Villarreal","away":"Juventus","hg":2,"ag":2},
    # Matchday 3 - Oct 21
    {"date":"2025-10-21","home":"Barcelona","away":"Olympiacos","hg":6,"ag":1},
    {"date":"2025-10-21","home":"Kairat Almaty","away":"Pafos","hg":0,"ag":0},
    {"date":"2025-10-21","home":"Arsenal","away":"Atlético de Madrid","hg":4,"ag":0},
    {"date":"2025-10-21","home":"Leverkusen","away":"Paris Saint-Germain","hg":2,"ag":7},
    {"date":"2025-10-21","home":"Copenhagen","away":"Borussia Dortmund","hg":2,"ag":4},
    {"date":"2025-10-21","home":"Newcastle United","away":"Benfica","hg":3,"ag":0},
    {"date":"2025-10-21","home":"PSV Eindhoven","away":"Napoli","hg":6,"ag":2},
    {"date":"2025-10-21","home":"Union Saint-Gilloise","away":"Inter","hg":0,"ag":4},
    {"date":"2025-10-21","home":"Villarreal","away":"Manchester City","hg":0,"ag":2},
    # Matchday 3 - Oct 22
    {"date":"2025-10-22","home":"Athletic Club","away":"Qarabağ","hg":3,"ag":1},
    {"date":"2025-10-22","home":"Galatasaray","away":"Bodø/Glimt","hg":3,"ag":1},
    {"date":"2025-10-22","home":"Monaco","away":"Tottenham","hg":0,"ag":0},
    {"date":"2025-10-22","home":"Atalanta","away":"Slavia Praha","hg":0,"ag":0},
    {"date":"2025-10-22","home":"Chelsea","away":"Ajax","hg":5,"ag":1},
    {"date":"2025-10-22","home":"Frankfurt","away":"Liverpool","hg":1,"ag":5},
    {"date":"2025-10-22","home":"Bayern München","away":"Club Brugge","hg":4,"ag":0},
    {"date":"2025-10-22","home":"Real Madrid","away":"Juventus","hg":1,"ag":0},
    {"date":"2025-10-22","home":"Sporting CP","away":"Marseille","hg":2,"ag":1},
    # Matchday 4 - Nov 4
    {"date":"2025-11-04","home":"Slavia Praha","away":"Arsenal","hg":0,"ag":3},
    {"date":"2025-11-04","home":"Napoli","away":"Frankfurt","hg":0,"ag":0},
    {"date":"2025-11-04","home":"Atlético de Madrid","away":"Union Saint-Gilloise","hg":3,"ag":1},
    {"date":"2025-11-04","home":"Bodø/Glimt","away":"Monaco","hg":0,"ag":1},
    {"date":"2025-11-04","home":"Juventus","away":"Sporting CP","hg":1,"ag":1},
    {"date":"2025-11-04","home":"Liverpool","away":"Real Madrid","hg":1,"ag":0},
    {"date":"2025-11-04","home":"Olympiacos","away":"PSV Eindhoven","hg":1,"ag":1},
    {"date":"2025-11-04","home":"Paris Saint-Germain","away":"Bayern München","hg":1,"ag":2},
    {"date":"2025-11-04","home":"Tottenham","away":"Copenhagen","hg":4,"ag":0},
    # Matchday 4 - Nov 5
    {"date":"2025-11-05","home":"Pafos","away":"Villarreal","hg":1,"ag":0},
    {"date":"2025-11-05","home":"Qarabağ","away":"Chelsea","hg":2,"ag":2},
    {"date":"2025-11-05","home":"Ajax","away":"Galatasaray","hg":0,"ag":3},
    {"date":"2025-11-05","home":"Club Brugge","away":"Barcelona","hg":3,"ag":3},
    {"date":"2025-11-05","home":"Inter","away":"Kairat Almaty","hg":2,"ag":1},
    {"date":"2025-11-05","home":"Manchester City","away":"Borussia Dortmund","hg":4,"ag":1},
    {"date":"2025-11-05","home":"Newcastle United","away":"Athletic Club","hg":2,"ag":0},
    {"date":"2025-11-05","home":"Marseille","away":"Atalanta","hg":0,"ag":1},
    {"date":"2025-11-05","home":"Benfica","away":"Leverkusen","hg":0,"ag":1},
    # Matchday 5 - Nov 25
    {"date":"2025-11-25","home":"Ajax","away":"Benfica","hg":0,"ag":2},
    {"date":"2025-11-25","home":"Galatasaray","away":"Union Saint-Gilloise","hg":0,"ag":1},
    {"date":"2025-11-25","home":"Borussia Dortmund","away":"Villarreal","hg":4,"ag":0},
    {"date":"2025-11-25","home":"Chelsea","away":"Barcelona","hg":3,"ag":0},
    {"date":"2025-11-25","home":"Bodø/Glimt","away":"Juventus","hg":2,"ag":3},
    {"date":"2025-11-25","home":"Manchester City","away":"Leverkusen","hg":0,"ag":2},
    {"date":"2025-11-25","home":"Marseille","away":"Newcastle United","hg":2,"ag":1},
    {"date":"2025-11-25","home":"Slavia Praha","away":"Athletic Club","hg":0,"ag":0},
    {"date":"2025-11-25","home":"Napoli","away":"Qarabağ","hg":2,"ag":0},
    # Matchday 6 - Dec 9
    {"date":"2025-12-09","home":"Kairat Almaty","away":"Olympiacos","hg":0,"ag":1},
    {"date":"2025-12-09","home":"Bayern München","away":"Sporting CP","hg":3,"ag":1},
    {"date":"2025-12-09","home":"Monaco","away":"Galatasaray","hg":1,"ag":0},
    {"date":"2025-12-09","home":"Atalanta","away":"Chelsea","hg":2,"ag":1},
    {"date":"2025-12-09","home":"Barcelona","away":"Frankfurt","hg":2,"ag":1},
    {"date":"2025-12-09","home":"Inter","away":"Liverpool","hg":0,"ag":1},
    {"date":"2025-12-09","home":"PSV Eindhoven","away":"Atlético de Madrid","hg":2,"ag":3},
    {"date":"2025-12-09","home":"Union Saint-Gilloise","away":"Marseille","hg":2,"ag":3},
    # Matchday 6 - Dec 10
    {"date":"2025-12-10","home":"Qarabağ","away":"Ajax","hg":2,"ag":4},
    {"date":"2025-12-10","home":"Villarreal","away":"Copenhagen","hg":2,"ag":3},
    {"date":"2025-12-10","home":"Athletic Club","away":"Paris Saint-Germain","hg":0,"ag":0},
    {"date":"2025-12-10","home":"Leverkusen","away":"Newcastle United","hg":2,"ag":2},
    {"date":"2025-12-10","home":"Borussia Dortmund","away":"Bodø/Glimt","hg":2,"ag":2},
    {"date":"2025-12-10","home":"Club Brugge","away":"Arsenal","hg":0,"ag":3},
    {"date":"2025-12-10","home":"Juventus","away":"Pafos","hg":2,"ag":0},
    {"date":"2025-12-10","home":"Real Madrid","away":"Manchester City","hg":1,"ag":2},
    {"date":"2025-12-10","home":"Benfica","away":"Napoli","hg":2,"ag":0},
    # Matchday 8 - Jan 28
    {"date":"2026-01-28","home":"Ajax","away":"Olympiacos","hg":1,"ag":2},
    {"date":"2026-01-28","home":"Arsenal","away":"Kairat Almaty","hg":3,"ag":2},
    {"date":"2026-01-28","home":"Monaco","away":"Juventus","hg":0,"ag":0},
    {"date":"2026-01-28","home":"Athletic Club","away":"Sporting CP","hg":2,"ag":3},
    {"date":"2026-01-28","home":"Atlético de Madrid","away":"Bodø/Glimt","hg":1,"ag":2},
    {"date":"2026-01-28","home":"Leverkusen","away":"Villarreal","hg":3,"ag":0},
    {"date":"2026-01-28","home":"Borussia Dortmund","away":"Inter","hg":0,"ag":2},
    {"date":"2026-01-28","home":"Club Brugge","away":"Marseille","hg":3,"ag":0},
    {"date":"2026-01-28","home":"Frankfurt","away":"Tottenham","hg":0,"ag":2},
    {"date":"2026-01-28","home":"Barcelona","away":"Copenhagen","hg":4,"ag":1},
    {"date":"2026-01-28","home":"Liverpool","away":"Qarabağ","hg":6,"ag":0},
    {"date":"2026-01-28","home":"Manchester City","away":"Galatasaray","hg":2,"ag":0},
    {"date":"2026-01-28","home":"Pafos","away":"Slavia Praha","hg":4,"ag":1},
    {"date":"2026-01-28","home":"Paris Saint-Germain","away":"Newcastle United","hg":1,"ag":1},
    {"date":"2026-01-28","home":"PSV Eindhoven","away":"Bayern München","hg":1,"ag":2},
    {"date":"2026-01-28","home":"Union Saint-Gilloise","away":"Atalanta","hg":1,"ag":0},
]

# Europa League - Fenerbahce matches
el_fenerbahce = [
    {"date":"2025-09-25","home":"Fenerbahce","away":"Sparta Praha","hg":2,"ag":1},
    {"date":"2025-10-02","home":"Real Betis","away":"Fenerbahce","hg":1,"ag":1},
    {"date":"2025-10-23","home":"Fenerbahce","away":"Olympique Lyon","hg":3,"ag":0},
    {"date":"2025-11-06","home":"West Ham United","away":"Fenerbahce","hg":2,"ag":0},
    {"date":"2025-11-27","home":"Fenerbahce","away":"Sporting CP","hg":1,"ag":2},
    {"date":"2025-12-11","home":"Fenerbahce","away":"Nottingham Forest","hg":0,"ag":3},
]

# Europa League - Nottingham Forest matches (Fenerbahce dışı)
el_forest = [
    {"date":"2025-09-25","home":"Nottingham Forest","away":"Rangers","hg":2,"ag":0},
    {"date":"2025-10-02","home":"Fiorentina","away":"Nottingham Forest","hg":1,"ag":2},
    {"date":"2025-10-23","home":"Nottingham Forest","away":"AZ Alkmaar","hg":1,"ag":1},
    {"date":"2025-11-06","home":"Villarreal","away":"Nottingham Forest","hg":2,"ag":2},
    # 2025-11-27 Forest vs Fenerbahce is same as Fenerbahce entry but reversed - skip duplicate
    # {"date":"2025-11-27","home":"Nottingham Forest","away":"Fenerbahce","hg":3,"ag":0},
    # This is listed from Fenerbahce perspective as away, but the Forest JSON says
    # home=Nott Forest vs away=Fenerbahce 3-0 on Nov 27
    # Fenerbahce JSON says home=Fenerbahce away=Sporting CP on Nov 27 - different match
    # Actually checking: Fenerbahce JSON has Dec 11 Forest match. Forest JSON Nov 27 is different.
]

# Actually, let me re-check: Fenerbahce has "Fenerbahce vs Nottingham Forest 0-3" on Dec 11
# Forest has "Nottingham Forest vs Fenerbahce 3-0" on Nov 27
# These are TWO different matches (home and away legs)
# So the Nov 27 Forest match should be added
el_forest_extra = [
    {"date":"2025-11-27","home":"Nottingham Forest","away":"Fenerbahce","hg":3,"ag":0},
]

all_new_matches = cl_matches + el_fenerbahce + el_forest + el_forest_extra

# --- CSV'ye dönüştür ---
new_rows = []
for m in all_new_matches:
    home = map_team_name(m["home"])
    away = map_team_name(m["away"])
    new_rows.append({
        "tarih": m["date"],
        "ev_sahibi": home,
        "deplasman": away,
        "ev_gol": m["hg"],
        "dep_gol": m["ag"]
    })

df_new = pd.DataFrame(new_rows)

# --- Duplikasyon Kontrolü ---
# Mevcut CSV'deki maçlarla karşılaştır
df_existing['key'] = df_existing['tarih'].astype(str) + '|' + df_existing['ev_sahibi'] + '|' + df_existing['deplasman']
df_new['key'] = df_new['tarih'].astype(str) + '|' + df_new['ev_sahibi'] + '|' + df_new['deplasman']

existing_keys = set(df_existing['key'].values)
df_truly_new = df_new[~df_new['key'].isin(existing_keys)].copy()
df_truly_new = df_truly_new.drop(columns=['key'])

skipped = len(df_new) - len(df_truly_new)
print(f"\n📊 Toplam {len(df_new)} maç işlendi:")
print(f"   ⏭️  {skipped} maç zaten mevcut (atlandı)")
print(f"   ✅ {len(df_truly_new)} yeni maç eklenecek")

if len(df_truly_new) > 0:
    # Yeni takımları göster
    new_teams_home = set(df_truly_new['ev_sahibi'].unique())
    new_teams_away = set(df_truly_new['deplasman'].unique())
    all_new_teams = (new_teams_home | new_teams_away) - existing_teams
    if all_new_teams:
        print(f"\n🆕 Yeni takımlar (modelin bilmediği):")
        for t in sorted(all_new_teams):
            print(f"   - {t}")

    # CSV'ye ekle
    df_existing = df_existing.drop(columns=['key'])
    df_combined = pd.concat([df_existing, df_truly_new], ignore_index=True)
    df_combined.to_csv(CSV_PATH, index=False)
    print(f"\n💾 CSV güncellendi! Toplam satır: {len(df_combined)}")
else:
    print("\n⚠️ Eklenecek yeni maç bulunamadı.")

print("\n✨ İşlem tamamlandı!")
