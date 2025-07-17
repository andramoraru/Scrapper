import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_stackoverflow_duckduckgo(query, max_results=5):
    url = f"https://html.duckduckgo.com/html/?q=site:stackoverflow.com+{urllib.parse.quote_plus(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(url, headers=headers)  
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    links = soup.select("a.result__a")[:max_results]

    for link in links:
        title = link.get_text(strip=True)
        href = link.get("href")
        results.append({
            "title": title,
            "url": href
        })

    return results

if __name__ == "__main__":
    q = input("Cauta pe Stack Overflow: ").strip()
    rezultate = search_stackoverflow_duckduckgo(q)
    if rezultate:
        for r in rezultate:
            print(f"- {r['title']}\n  {r['url']}\n")
    else:
        print("Niciun rezultat gasit.")
