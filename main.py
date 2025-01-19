from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time

# Şehir kodlarını dosyadan okuma fonksiyonu
def load_city_codes(file_path):
    city_codes = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                city_codes[int(parts[0].strip())] = parts[1].strip()
    return city_codes

# Şehir kodlarını yükle
city_codes = load_city_codes("city_codes.txt")

# Kullanıcıdan kalkış ve varış şehirlerini seçmesini iste
print("Şehir Kodları:")
for code, name in city_codes.items():
    print(f"{code}: {name}")

origin_code = int(input("\nKalkış Şehri Kodunu Girin: "))
destination_code = int(input("Varış Şehri Kodunu Girin: "))

# Tarih aralığı
start_date = datetime.today()
num_days = 10  # Kaç gün kontrol edilecek

# Chrome tarayıcı seçenekleri
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")  # Tarayıcıyı gizli modda çalıştırmak için
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriver'ı başlat
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Fiyatları depolamak için bir liste
all_data = []

try:
    for day_offset in range(num_days):
        # Tarihi hesapla
        date = start_date + timedelta(days=day_offset)
        formatted_date = date.strftime("%Y-%m-%d")

        # URL'yi oluştur
        url = f"https://www.obilet.com/seferler/{origin_code}-{destination_code}/{formatted_date}"
        print(f"Kontrol edilen tarih ve URL: {formatted_date} - {url}")

        # Sayfayı aç
        driver.get(url)
        time.sleep(5)  # Dinamik içeriklerin yüklenmesi için bekle

        # Günlük verileri topla
        try:
            companies = driver.find_elements(By.CLASS_NAME, "partner-logo")
            departures = driver.find_elements(By.CLASS_NAME, "departure")
            durations = driver.find_elements(By.CLASS_NAME, "duration")
            prices = driver.find_elements(By.CLASS_NAME, "amount-integer")

            for i in range(len(prices)):
                company = companies[i].get_attribute("data-name") if i < len(companies) else "N/A"
                departure = departures[i].text if i < len(departures) else "N/A"
                duration = durations[i].text if i < len(durations) else "N/A"
                price = int(prices[i].text) if i < len(prices) else float('inf')
                all_data.append((formatted_date, company, departure, duration, price, url))
        except Exception as e:
            print(f"Veri alınamadı: {e}")

    # En ucuz bileti bul
    if all_data:
        all_data.sort(key=lambda x: x[4])  # Fiyata göre sırala
        cheapest = all_data[0]

        print("\nEn Ucuz Bilet:")
        print(f"Tarih: {cheapest[0]}")
        print(f"Firma: {cheapest[1]}")
        print(f"Kalkış Saati: {cheapest[2]}")
        print(f"Süre: {cheapest[3]}")
        print(f"Fiyat: {cheapest[4]} TL")
        print(f"Link: {cheapest[5]}")
    else:
        print("Hiçbir veri bulunamadı!")

finally:
    # Tarayıcıyı kapat
    driver.quit()
