import requests
from bs4 import BeautifulSoup
import urllib.parse
from db_manager import insert_product, insert_price  

def search_cel(query, max_results=5):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.cel.ro/cauta/{encoded_query}"

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        results = []
        containers = soup.find_all("div", class_="product_data", limit=max_results)

        for container in containers:
         title_tag = container.find("a", class_="product_link")
         name = title_tag.text.strip() if title_tag else "Fără titlu"
         link = title_tag["href"] if title_tag else "#"
         if not link.startswith("http"):
             link = urllib.parse.urljoin("https://www.cel.ro", link)

         price_tag = container.find("span", class_="price")
         price = float(price_tag.text.replace(".", "").replace(",", ".").strip()) if price_tag else 0.0

         parent = container.parent
         image_tag = parent.find("img") if parent else None
         image_url = ""
         if image_tag:
            image_url = image_tag.get("src") or image_tag.get("data-original") or ""
            if not image_url.startswith("http"):
              image_url = urllib.parse.urljoin("https://www.cel.ro", image_url)

         insert_product(name, "CEL", link)
         insert_price(link, price)

         results.append({
           "name": name,
           "price": price,
            "url": link,
           "image": image_url
         })


        return results

    except Exception as e:
        print(f"Eroare la scraping CEL.ro: {e}")
        return []

if __name__ == "__main__":
    query = input("Cauta pe CEL.ro: ").strip()
    results = search_cel(query)
    if results:
        for i, p in enumerate(results, 1):
            print(f"{i}. {p['name']}")
            print(f"   {p['price']} RON")
            print(f"   {p['url']}")
            print(f"   Imagine: {p['image']}\n")
    else:
        print("Niciun produs gasit.")