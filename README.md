# 🧠 AutoScout AI Pro: Akıllı Araç Yatırım Asistanı

AutoScout AI Pro, otomobil ve motosiklet ilanlarını web kazıma (web scraping) yöntemleriyle toplayan, verileri temizleyen ve **Makine Öğrenmesi (Random Forest)** algoritmaları kullanarak piyasa analizi yapan gelişmiş bir yatırım asistanıdır.

## 🚀 Öne Çıkan Özellikler

* **Dinamik Web Scraping:** Selenium tabanlı bot ile birden fazla kategoride (Otomobil, Motosiklet, SUV vb.) güncel ilan verisi toplama.
* **AI Fiyat Tahmini:** Araçların yılı ve kilometresine göre olması gereken piyasa değerini hesaplayan eğitilmiş model.
* **Yatırım Fırsatları:** Piyasa değerinin altında kalan "Fırsat" araçları otomatik olarak tespit edip ön plana çıkarma.
* **Gelişmiş Filtreleme:** Kullanıcı dostu arayüz ile bütçe, kilometre ve kategori bazlı hassas arama.
* **İnteraktif Piyasa Analizi:** Plotly kütüphanesi ile hazırlanan fiyat yoğunluğu ve potansiyel kâr grafikleri.

## 🛠️ Kullanılan Teknolojiler

* **Dil:** Python
* **Arayüz:** Streamlit
* **Veri Kazıma:** Selenium & WebDriver Manager
* **Veri Analizi:** Pandas & NumPy
* **Makine Öğrenmesi:** Scikit-learn (Random Forest Regressor)
* **Veri Depolama:** Google Sheets API (gspread)
* **Görselleştirme:** Plotly

## 📦 Kurulum

1.  **Depoyu Klonlayın:**
    ```bash
    git clone [https://github.com/kullanici-adin/arac-yatirim-asistani.git](https://github.com/kullanici-adin/arac-yatirim-asistani.git)
    cd arac-yatirim-asistani
    ```

2.  **Gerekli Kütüphaneleri Kurun:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Google API Yapılandırması:**
    * Google Cloud Console üzerinden bir Service Account oluşturun.
    * `credentials.json` dosyasını ana dizine ekleyin (Güvenlik nedeniyle `.gitignore` listesindedir).
    * İlgili Google Sheet dosyasını Service Account e-postası ile paylaşın.

4.  **Uygulamayı Çalıştırın:**
    ```bash
    streamlit run app.py
    ```
