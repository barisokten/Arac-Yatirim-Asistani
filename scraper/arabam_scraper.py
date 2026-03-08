import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os

# ---------- AYARLAR ----------
PAGES_PER_CATEGORY = 5  # Her kategoriden kaç sayfa çekilsin? (5 x 50 = 250 ilan kategori başı)
SHEET_NAME = "arabam_data"
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")

# KATEGORİ LİSTESİ ()
CATEGORIES = {
    "Otomobil": "https://www.arabam.com/ikinci-el/otomobil",
    "Arazi, SUV & Pick-up": "https://www.arabam.com/ikinci-el/arazi-suv-pick-up",
    "Motosiklet": "https://www.arabam.com/ikinci-el/motosiklet",
    "Minivan & Panelvan": "https://www.arabam.com/ikinci-el/minivan-panelvan",
    "Ticari Araçlar": "https://www.arabam.com/ikinci-el/ticari-araclar",
    "Hasarlı Araçlar": "https://www.arabam.com/ikinci-el/hasarli-araclar"
}

KNOWN_COLORS = ["Beyaz", "Siyah", "Gri", "Gümüş", "Kırmızı", "Mavi", "Lacivert", "Yeşil", "Sarı", "Bej", "Kahverengi", "Turuncu", "Mor", "Şampanya", "Füme", "Bronz"]

# ---------- GOOGLE BAĞLANTISI ----------
print("🔌 Google Sheets'e bağlanılıyor...")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1
print("✅ Bağlantı Başarılı!")

# Başlıkları Yenile (Yeni 'category' sütunu ekliyoruz)
sheet.clear()
sheet.append_row(["category", "image", "link", "title", "year", "km", "color", "price", "location"])

# ---------- SELENIUM ----------
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def scrape_category(category_name, base_url, max_pages):
    print(f"\n📂 KATEGORİ İŞLENİYOR: {category_name}")
    category_data = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}?take=50&page={page}"
        print(f"   └── Sayfa {page}/{max_pages} taranıyor...")
        
        try:
            driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            for row in rows:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", row)
                    time.sleep(0.05)
                    
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if not cols or len(cols) < 3: continue
                    col_texts = [c.text.strip() for c in cols]

                    # --- VERİ AYIKLAMA ---
                    color = "Belirtilmemiş"
                    for text in col_texts:
                        if text in KNOWN_COLORS:
                            color = text
                            break
                    
                    price = "0"
                    for text in col_texts:
                        if "TL" in text:
                            price = text.split("\n")[-1] if "\n" in text else text
                            break

                    km = "0"
                    for text in col_texts:
                        clean = text.replace(".", "")
                        # KM Algoritması ()
                        if clean.isdigit() and "TL" not in text and len(clean) < 7:
                             if int(clean) > 2026 or int(clean) < 1900: 
                                km = clean
                                break
                    
                    year = "0"
                    for text in col_texts[:5]:
                        if text.isdigit() and len(text) == 4 and (text.startswith("20") or text.startswith("19")):
                            year = text
                            break

                    title = "Başlık Yok"
                    location = ""
                    sorted_texts = sorted(col_texts, key=len, reverse=True)
                    for t in sorted_texts:
                        if "TL" not in t and t != location and t != color:
                            title = t.replace("\n", " ")
                            break
                    if len(col_texts) > 0: location = col_texts[-1].replace("\n", " ")

                    image_url = "https://via.placeholder.com/200"
                    try:
                        img_tag = row.find_element(By.TAG_NAME, "img")
                        src = img_tag.get_attribute("src")
                        if not src or "base64" in src or "assets" in src: src = img_tag.get_attribute("data-src")
                        if src: image_url = src
                    except: pass

                    # --- AKILLI LİNK AYIKLAMA ---
                    link_url = base_url
                    try:
                        # Satır içindeki tüm linkleri (<a> etiketlerini) bul
                        all_links = row.find_elements(By.TAG_NAME, "a")
                        
                        for l in all_links:
                            href = l.get_attribute("href")
                            if href:
                                # Sadece gerçek ilan detayına giden linki seç (İçinde 'ilan' veya 'detay' geçmeli)
                                if "/ilan/" in href or "/detay/" in href:
                                    link_url = href if href.startswith("http") else "https://www.arabam.com" + href
                                    break
                    except Exception as e:
                        print(f"      ⚠️ Link yakalanamadı: {e}")
                except: continue
        except Exception as e:
            print(f"   Hata: {e}")
    
    return category_data

# ---------- ANA DÖNGÜ ----------
try:
    total_saved = 0
    
    # Her kategoriyi tek tek gez
    for cat_name, cat_url in CATEGORIES.items():
        data = scrape_category(cat_name, cat_url, PAGES_PER_CATEGORY)
        
        if data:
            print(f"   ☁️ {len(data)} adet {cat_name} Google Sheets'e yükleniyor...")
            sheet.append_rows(data)
            total_saved += len(data)
            print("   ✔ Kaydedildi.")
        
        time.sleep(2)

finally:
    driver.quit()
    print(f"\n🎉 TÜM İŞLEM BİTTİ! Toplam {total_saved} ilan sınıflandırılarak kaydedildi.")