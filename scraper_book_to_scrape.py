import requests
from bs4 import BeautifulSoup

def get_books(query, max_pages=2):
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    results = []

    for page in range(1, max_pages + 1):
        try:
            url = base_url.format(page)
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            books = soup.find_all("article", class_="product_pod")

            for book in books:
                title = book.h3.a["title"]
                price_tag = book.find("p", class_="price_color")
                if not price_tag:
                    continue
                price_str = price_tag.text.strip()
                price_str = price_str.replace("Â", "").replace("£", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    print(f"Eroare la pagina {page}: {price_str}")
                    continue

                if query.lower() in title.lower():
                    results.append({
                        "title": title,
                        "price": price
                    })

        except Exception as e:
            print(f"Eroare la pagina {page}: {e}")

    return results

if __name__ == "__main__":
    print("Cautare carti pe BooksToScrape.com\n")
    q = input("Introdu un cuvant cheie (ex: science, travel, mystery): ").strip()

    if not q:
        print(" Nu ai introdus nimic.")
    else:
        books = get_books(q)
        if books:
            print(f"\nGăsite {len(books)} rezultate pentru: '{q}'\n")
            for i, b in enumerate(books, 1):
                print(f"{i}. {b['title']} —  {b['price']} £")
        else:
            print(" Nicio carte găsită.")
