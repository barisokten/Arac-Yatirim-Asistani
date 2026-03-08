1. Veri Kazıma ve Temizlik Stratejisi

Dinamik Veri Çekme: Selenium kullanılarak sayfa kaydırma (scroll) simülasyonu ile lazy-load görsellerin ve gizli linklerin tam doğrulukla çekilmesi sağlandı.

Gelişmiş Metin İşleme (Regex): "1.250.000 TL" veya "Fiyat Sorunuz" gibi karmaşık metin girişleri, düzenli ifadeler (Regex) kullanılarak saf sayısal verilere dönüştürüldü.

Aykırı Değer (Outlier) Yönetimi: Hatalı girilen (örneğin 70 Milyon TL'lik Berlingo gibi) veya piyasa gerçekliğinden uzak uçuk rakamlar, istatistiksel filtreleme ile analiz dışı bırakıldı.

2. Makine Öğrenmesi Modeli (Random Forest)

Model Seçimi: Doğrusal olmayan ilişkileri (yaş ve kilometre arasındaki karmaşık bağ) daha iyi yakaladığı için RandomForestRegressor tercih edildi.

Özellik Mühendisliği (Feature Engineering): Model; aracın yılı, kilometresi ve kategorisi üzerinden bir "Rayiç Bedel" hesaplar.

Fırsat Skoru Algoritması: $Tahmin Edilen Fiyat - İlan Fiyatı$ formülü kullanılarak, piyasa değerinin en çok altında kalan araçlar "Yatırım Fırsatı" olarak etiketlenir.

3. Kullanıcı Deneyimi ve Görselleştirme

Veri Formatlama: Tüm finansal veriler Türkiye standartlarına uygun olarak (her 3 basamakta bir nokta) format_tl fonksiyonu ile görselleştirildi.

İnteraktif Dashboard: Plotly kütüphanesi ile kullanıcıya sadece liste değil, seçili filtreler içindeki fiyat yoğunluğunu gösteren dinamik grafikler sunuldu.