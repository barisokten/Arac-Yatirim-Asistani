import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import os
from sklearn.ensemble import RandomForestRegressor


st.set_page_config(page_title="AutoScout AI Pro", page_icon="🧠", layout="wide")

# --- TASARIM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #0E1117; }
    
    div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
        background-color: #161B22; border-radius: 15px; padding: 15px; border: 1px solid #30363D;
    }
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #4CAF50, #8BC34A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 24px; font-weight: 800;
    }
    .badge-firsat {
        background-color: #00b894; color: white; padding: 6px 12px; border-radius: 12px; font-size: 13px; font-weight: bold;
    }
    .badge-kategori {
        background-color: #0984e3; color: white; padding: 4px 8px; border-radius: 6px; font-size: 11px; margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
@st.cache_data(ttl=600)
def load_data_from_sheets():
    try:
        json_path = os.path.join("scraper", "credentials.json") 
        if not os.path.exists(json_path): json_path = "credentials.json"
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
        client = gspread.authorize(creds_dict)
        sheet = client.open("arabam_data").sheet1
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        return None

def clean_currency(value):
    if pd.isna(value): return 0
    clean_str = re.sub(r'[^\d]', '', str(value))
    try: return int(clean_str)
    except: return 0

def extract_engine(title):
    match = re.search(r"\b[0-6]\.\d\b", str(title))
    if match: return match.group(0)
    return "Diğer"

def format_tl(value):
    if value is None or value == 0:
        return "Fiyat Sorunuz"
    return f"{int(value):,}".replace(",", ".") + " TL"

# --- AI ---
def train_ai_model(df):
    if len(df) < 5: return None 
    X = df[['yil_sayi', 'km_sayi']]
    y = df['fiyat_sayi']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# --- VERİ HAZIRLIĞI ---
df_raw = load_data_from_sheets()
if df_raw is None or df_raw.empty:
    st.warning("Veri yok.")
    st.stop()

df = df_raw.copy()
df["fiyat_sayi"] = df["price"].apply(clean_currency)
df["yil_sayi"] = df["year"].apply(clean_currency)
df["km_sayi"] = df["km"].apply(clean_currency)
df["motor"] = df["title"].apply(extract_engine)
if "category" not in df.columns: df["category"] = "Genel" # Hata önleyici

# Temizlik
df = df[(df["fiyat_sayi"] > 50000) & (df["fiyat_sayi"] < 15000000)]

# --- YAN MENÜ ---
with st.sidebar:
    st.header("🚘 Filtreler")
    
    # 1. KATEGORİ SEÇİMİ ()
    kategoriler = ["Tümü"] + sorted(df["category"].unique().tolist())
    secilen_kategori = st.selectbox("📂 Kategori Seç", kategoriler)
    
    st.markdown("---")
    
    # 2. MODEL ARAMA
    arama_kelimesi = st.text_input("🔍 Marka/Model Ara", placeholder="Örn: Civic")
    st.markdown("---")
    # BÜTÇE KISMI GÜNCELLEME
    min_v = int(df["fiyat_sayi"].min())
    # Sabit 100M sınırı
    max_v = 100000000  

    butce_araligi = st.slider(
        "💰 Bütçe Aralığı", 
        min_value=0, 
        max_value=max_v, 
        value=(min_v, 5000000), 
        step=50000,
        format="%d" # Slider üzerindeki rakamları düz sayı olarak tutar
    )
    st.markdown(f"""
        <div style='background-color: #1e2130; padding: 10px; border-radius: 5px; border: 1px solid #3e4251; text-align: center;'>
            <span style='color: #4CAF50; font-weight: bold;'>{format_tl(butce_araligi[0])}</span> 
            <span style='color: white;'> - </span> 
            <span style='color: #4CAF50; font-weight: bold;'>{format_tl(butce_araligi[1])}</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
  
    mevcut_renkler = sorted([r for r in df["color"].unique() if str(r) != "nan"])
    secilen_renkler = st.multiselect("🎨 Renk", mevcut_renkler)
    yil_araligi = st.slider("📅 Yıl", 1990, 2025, (2010, 2025))


    st.markdown("---")
    st.header("🛣️ Kilometre Seçimi")
    
    # 1.000.000 KM sınır ve temizleme
    max_km_sinir = 1000000
    min_km_veri = int(df["km_sayi"].min())
    
    km_araligi = st.slider(
        "🚗 Kilometre Aralığı",
        min_value=0,
        max_value=max_km_sinir,
        value=(0, 250000), # Varsayılan 250 bin km altı araçlar
        step=5000,
        format="%d"
    )

    # Kilometre için de format_tl benzeri bir gösterim 
    def format_km(val):
        return f"{int(val):,}".replace(",", ".") + " km"

    st.markdown(f"""
        <div style='background-color: #161b22; padding: 10px; border-radius: 5px; border: 1px solid #30363d; text-align: center;'>
            <span style='color: #0984e3; font-weight: bold;'>{format_km(km_araligi[0])}</span> 
            <span style='color: white;'> - </span> 
            <span style='color: #0984e3; font-weight: bold;'>{format_km(km_araligi[1])}</span>
        </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    st.header("📊 Akıllı Analiz")
    piyasa_analiz_aktif = st.toggle("Piyasa Analizi ve Fırsat Skoru")
    
    if piyasa_analiz_aktif:
        st.info("💡 AI Modeli: Mevcut filtrelere göre en kârlı araçları hesaplıyor.")


# --- FİLTRELEME ---
# Kategori Filtresi
if secilen_kategori != "Tümü":
    cat_filter = df["category"] == secilen_kategori
else:
    cat_filter = True

# Arama Filtresi
if arama_kelimesi:
    text_filter = df["title"].str.contains(arama_kelimesi, case=False, na=False)
else:
    text_filter = True

renk_filtresi = True if not secilen_renkler else df["color"].isin(secilen_renkler)

filtrelenmis = df[
    cat_filter & text_filter & renk_filtresi &
    (df["fiyat_sayi"] >= butce_araligi[0]) & (df["fiyat_sayi"] <= butce_araligi[1]) &
    (df["yil_sayi"] >= yil_araligi[0]) & (df["yil_sayi"] <= yil_araligi[1])&
    (df["km_sayi"] >= km_araligi[0]) & (df["km_sayi"] <= km_araligi[1]) # Yeni Filtre
]

# --- YAN MENÜ () ---
with st.sidebar:
    st.markdown("---")
    st.header("📊 Analiz Araçları")
    analiz_modu = st.toggle("Piyasa Analiz Panelini Aç", help="Seçili filtrelere göre piyasa özetini gösterir.")


# AI Analizi
en_iyi_firsat_miktari = 0
en_iyi_firsat_linki = None
if len(filtrelenmis) > 5:
    model = train_ai_model(filtrelenmis)
    if model:
        filtrelenmis['ai_deger'] = model.predict(filtrelenmis[['yil_sayi', 'km_sayi']])
        filtrelenmis['fark'] = filtrelenmis['ai_deger'] - filtrelenmis['fiyat_sayi']
        filtrelenmis = filtrelenmis.sort_values(by='fark', ascending=False)
        top_car = filtrelenmis.iloc[0]
        if top_car['fark'] > 0:
            en_iyi_firsat_miktari = top_car['fark']
            en_iyi_firsat_linki = top_car['link']

# --- ARAYÜZ ---
st.title("🧠 Araç Yatırım Asistanı")

# --- PİYASA ANALİZ PANELİ (Ana Sayfa) ---
if analiz_modu and not filtrelenmis.empty:
    st.markdown("### 📈 Seçili Filtrelerin Piyasa Özeti")
    
    # 1. Satır: Temel İstatistik Metrikleri
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("En Ucuz", format_tl(filtrelenmis["fiyat_sayi"].min()))
    with a2:
        st.metric("Ortalama", format_tl(filtrelenmis["fiyat_sayi"].mean()))
    with a3:
        st.metric("En Pahalı", format_tl(filtrelenmis["fiyat_sayi"].max()))
    with a4:
        # Medyan fiyat ()
        st.metric("Medyan", format_tl(filtrelenmis["fiyat_sayi"].median()))

    # 2. Satır: Görsel Analiz (Plotly Histogram)
    st.markdown("#### 📊 Fiyat Yoğunluk Grafiği")
    import plotly.express as px
    
    # Fiyat dağılımını gösteren grafik
    fig = px.histogram(
        filtrelenmis, 
        x="fiyat_sayi", 
        nbins=30,
        color_discrete_sequence=['#4CAF50'],
        labels={'fiyat_sayi': 'Fiyat (TL)'},
        opacity=0.8
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    # 3. Satır: En İyi 3 Araç Tablosu
    st.markdown("#### 🏆 En Yüksek Yatırım Potansiyeli (Top 3)")
    # AI modelindeki 'fark' (ai_tahmini - gerçek_fiyat) sütununa göre en yüksekleri seçer
    if 'fark' in filtrelenmis.columns:
        firsatlar = filtrelenmis.sort_values(by="fark", ascending=False).head(3)
        st.dataframe(
            firsatlar[["title", "year", "km", "fiyat_sayi", "location","link"]],
            column_config={
                "title": "İlan Başlığı",
                "year": "Yıl",
                "km": "KM",
                "fiyat_sayi": st.column_config.NumberColumn("Fiyat", format="%d TL"),
                "link": st.column_config.LinkColumn(
                    "İlana Git ↗",
                    display_text="İncele",  # Hücrede görünecek metin
                    help="İlanın orijinal sayfasına gider"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    
    st.markdown("---")


# Kategori Bilgisi Göster
if secilen_kategori != "Tümü":
    st.caption(f"Şu an sadece **{secilen_kategori}** kategorisindeki araçlar analiz ediliyor.")

m1, m2, m3 = st.columns(3)
m1.metric("İlan Sayısı", f"{len(filtrelenmis)}")
if not filtrelenmis.empty:
    avg_price = filtrelenmis['fiyat_sayi'].mean()
    m2.metric("Ortalama Fiyat", format_tl(avg_price)) 
    
    if en_iyi_firsat_miktari > 0:
        with m3:
            m3.metric("En İyi Fırsat", format_tl(en_iyi_firsat_miktari) + " Avantaj")
            if en_iyi_firsat_linki: 
                st.link_button("🚀 Fırsata Git", en_iyi_firsat_linki, type="primary")
    else:
        m3.metric("Fırsat", "Yok")

st.markdown("---")

# --- ARAYÜZ DÖNGÜSÜ ---
if not filtrelenmis.empty:
    for index, row in filtrelenmis.iterrows():
        with st.container():
            c_img, c_info, c_price = st.columns([2, 4, 2])
            with c_img:
                img = row['image'] if "http" in str(row['image']) else "https://via.placeholder.com/300x200"
                # Uyarıyı önlemek için use_container_width=True
                st.image(img, use_container_width=True) 
            with c_info:
                st.subheader(row['title'])
                st.markdown(f'<span class="badge-kategori">{row["category"]}</span>', unsafe_allow_html=True)
                
                if 'ai_deger' in row and row['fark'] > 0:
                    # Avantaj miktarını da format_tl ile gösteriyoruz
                    st.markdown(f'<div class="badge-firsat">🔥 {format_tl(row["fark"])} AVANTAJLI</div>', unsafe_allow_html=True)
                
                st.write(f"📍 {row['location']} | 📅 {row['year']} | 🚗 {row['km']} km")
            with c_price:
                st.markdown(f'<div class="gradient-text">{format_tl(row["fiyat_sayi"])}</div>', unsafe_allow_html=True)
                st.link_button("İlana Git ↗", row['link'], type="primary", use_container_width=True)

else:
    st.error("Araç bulunamadı.")