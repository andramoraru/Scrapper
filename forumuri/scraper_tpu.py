from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import urllib.parse
import time

def search_tpu(query, max_results=5):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.tpu.ro/cauta/?keyword={encoded_query}"

    options = FirefoxOptions()
    options.add_argument("--headless")
    options.set_preference("dom.webnotifications.enabled", False)

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    results = []
    try:
        driver.get(url)
        time.sleep(3)  

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.boxType1.padding15.clearfix"))
        )

        boxes = driver.find_elements(By.CSS_SELECTOR, "div.boxType1.padding15.clearfix")

        for box in boxes:
            try:
                link_tag = box.find_element(By.CSS_SELECTOR, "p.textLargeResponsive2.marginT10 a")
                title = link_tag.text.strip()
                href = link_tag.get_attribute("href")
                if not href.startswith("http"):
                    href = "https://www.tpu.ro" + href

                results.append({
                    "title": title,
                    "url": href
                })

                if len(results) >= max_results:
                    break
            except Exception:
                continue

    except Exception as e:
        print(f" Eroare la scraping TPU: {e}")
        with open("pagina_tpu_final.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(" Pagina salvata în pagina_tpu_final.html pentru analiza.")
    finally:
        driver.quit()

    return results


if __name__ == "__main__":
    q = input(" Cauta pe TPU (forum TPU.ro): ").strip()
    rezultate = search_tpu(q)
    if rezultate:
        for r in rezultate:
            print(f"- {r['title']}\n  🔗 {r['url']}\n")
    else:
        print(" Niciun rezultat gasit.")
