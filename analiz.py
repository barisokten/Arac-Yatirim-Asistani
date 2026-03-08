
import pandas as pd
import re

#  CSV Dosyasını Oku
csv_file = "arabam_data_10_sayfa.csv"
try:
    df = pd.read_csv(csv_file)
    print(f"✅ '{csv_file}' başarıyla yüklendi.")
except FileNotFoundError:
    print(f"❌ Hata: '{csv_file}' bulunamadı!")
    exit()

# --- FORMATLAMA FONKSİYONU () ---
def format_tl(value):
    if value is None or value == 0:
        return "Fiyat Sorunuz"
    return f"{int(value):,}".replace(",", ".") + " TL"

def clean_currency(value):
    if pd.isna(value): return 0
    clean_str = re.sub(r'[^\d]', '', str(value))
    return int(clean_str) if clean_str else 0

#  TEMİZLİK VE KISITLAMA
df["fiyat_temiz"] = df["price"].apply(clean_currency)
df["km_temiz"] = df["km"].apply(clean_currency)
df["yil_temiz"] = df["year"].apply(clean_currency)

# 100 Milyon TL üst sınır
df = df[(df["fiyat_temiz"] > 0) & (df["fiyat_temiz"] <= 100000000)]

# --- DEBUG EKRANI () ---
print("\n🔍 VERİ KONTROLÜ (İlk 5 Satır):")
print("-" * 50)
# Burada format_tl'yi tek tek değerlere uyguluyoruz
temp_df = df[["price", "fiyat_temiz"]].head().copy()
temp_df["fiyat_formatli"] = temp_df["fiyat_temiz"].apply(format_tl)
print(temp_df)
print("-" * 50)

#  KULLANICI ETKİLEŞİMİ
print(f"\n🚗 --- ARAÇ YATIRIM DANIŞMANI v2 --- 🚗")
print(f"Veritabanında 100M TL altı {len(df)} geçerli ilan var.\n")

while True:
    try:
        inp = input("Lütfen maksimum bütçenizi girin (TL): ")
        butce = int(re.sub(r'[^\d]', '', inp))
        break
    except ValueError:
        print("Lütfen geçerli bir sayı girin.")

# FİLTRELEME ()
uygun_araclar = df[df["fiyat_temiz"] <= butce].copy()

# SIRALAMA
onerilenler = uygun_araclar.sort_values(by=["yil_temiz", "km_temiz"], ascending=[False, True])

# 4. ADIM: SONUÇLARI GÖSTER
if len(onerilenler) > 0:
    # Bütçeyi formatlı gösterelim
    print(f"\n🎉 Bütçenize ({format_tl(butce)}) uygun {len(onerilenler)} araç bulundu!")
    print("İşte en mantıklı ilk 10 yatırım fırsatı:\n")
    
    # Listeyi göstermeden önce fiyat sütununu formatlayalım
    onerilenler_display = onerilenler.head(10).copy()
    onerilenler_display["price"] = onerilenler_display["fiyat_temiz"].apply(format_tl)
    
    gosterilecek_sutunlar = ["title", "year", "km", "price", "location"]
    mevcut_sutunlar = [col for col in gosterilecek_sutunlar if col in df.columns]
    
    print(onerilenler_display[mevcut_sutunlar].to_string(index=False))
    
    # Excel'e kaydederken ham rakamları kaydederiz.
    dosya_adi = "butceme_uygun_arabalar.xlsx"
    onerilenler.to_excel(dosya_adi, index=False)
    print(f"\n✅ Ham liste '{dosya_adi}' dosyasına kaydedildi.")
else:
    print(f"\n😔 {format_tl(butce)} bütçeye uygun araç bulunamadı.")