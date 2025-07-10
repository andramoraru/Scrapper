
import requests
from bs4 import BeautifulSoup

def scrape_emag(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Cerere eșuată. Cod HTTP: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "lxml")

        # Nume produs
        name_tag = soup.find("h1")
        if not name_tag:
            print("Numele produsului nu a fost găsit.")
            return None
        name = name_tag.text.strip()
        price_tag = soup.find("p", class_="product-new-price")
        if not price_tag:
            print("Prețul nu a fost găsit.")
            return None

        raw_price = price_tag.text.strip().split()[0]

        price = float(raw_price.replace(".", "").replace(",", "."))
        
        return {
            "name": name,
            "price": price
        }

    except Exception as e:
        print(f"Eroare la scraping: {e}")
        return None

testAqua=scrape_emag("https://www.emag.ro/aquaclear-agent-de-limpezire-cu-vitamina-c-pentru-piscina-500g-18587-500g/pd/DLPDNK3BM/?ref=flashdeals_1_1&provider=flashdeals&recid=smart-deals-2025&scenario_ID=67")
print(testAqua)