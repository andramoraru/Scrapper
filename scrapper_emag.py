import requests
from bs4 import BeautifulSoup
import urllib.parse
from db_manager import insert_product, insert_price 
def search_emag_products(query, max_results=5):
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.emag.ro/search/{encoded_query}"
    headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
            )
    }

    try:
        response = requests.get(search_url,headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        product_blocks = soup.find_all("div", class_="card-item", limit=max_results)
        results = []

        for block in product_blocks:
            title_tag = block.find("a", href=True)
            price_tag = block.find("p", class_="product-new-price")
            img_tag = block.find("img")

            if not title_tag or not price_tag or not img_tag:
                continue

            name = img_tag.get("alt") or title_tag.text.strip()

            link = title_tag.get("href")
            if not link.startswith("http"):
                link = urllib.parse.urljoin("https://www.emag.ro", link)

            image_url = img_tag.get("src") or img_tag.get("data-src")
            if image_url and not image_url.startswith("http"):
                image_url = "https:" + image_url

            raw_price = price_tag.text.strip().split()[0]
            price = float(raw_price.replace(".", "").replace(",", "."))

            insert_product(name, "eMAG", link)
            insert_price(link, price)

            results.append({
                "name": name,
                "price": price,
                "url": link,
                "image": image_url
            })

        return results

    except Exception as e:
        print(f"Eroare la scraping eMAG: {e}")
        return []


if __name__ == "__main__":
    query = input("Cauta pe eMAG: ").strip()
    results = search_emag_products(query)
    if results:
        for i, p in enumerate(results, 1):
            print(f"{i}. {p['name']}")
            print(f"    {p['price']} RON")
            print(f"    {p['url']}\n")
    else:
        print("Niciun produs gasit.")
