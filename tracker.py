from scrapper_emag import search_emag
from scraper_cel import search_cel
from db_manager import insert_product, insert_price

def track(query):
    for site, search_func in [("eMAG", search_emag), ("CEL", search_cel)]:
        print(f"🔍 Cautare pe {site} pentru '{query}'...")
        products = search_func(query)
        for p in products:
            print(f"📦 {p['name']} - {p['price']} RON")
            insert_product(p['name'], site, p['url'])
            if p['price']:
                insert_price(p['url'], p['price'])

if __name__ == "__main__":
    q = input("Introdu produsul cautat: ").strip()
    track(q)
