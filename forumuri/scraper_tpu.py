import urllib.parse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

class TPUFinder:
    def __init__(self, headless: bool = True, timeout: int = 5):
        opts = FirefoxOptions()
        opts.headless = headless
        opts.set_preference("permissions.default.image", 2)
        opts.set_preference("permissions.default.stylesheet", 2)
        opts.set_preference("permissions.default.font", 2)
        opts.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")
        opts.set_preference("dom.webnotifications.enabled", False)
        opts.page_load_strategy = "eager"

        service = FirefoxService(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=opts)
        self.wait = WebDriverWait(self.driver, timeout)

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Perform a TPU.ro forum search and return up to max_results items
        as dicts {'title': ..., 'url': ...}.
        """
        q = urllib.parse.quote_plus(query)
        self.driver.get(f"https://www.tpu.ro/cauta/?keyword={q}")

        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.boxType1.padding15.clearfix")
        ))

        boxes = self.driver.find_elements(By.CSS_SELECTOR, "div.boxType1.padding15.clearfix")
        results = []
        for box in boxes[:max_results]:
            try:
                a = box.find_element(By.CSS_SELECTOR, "p.textLargeResponsive2.marginT10 a")
                title = a.text.strip()
                href = a.get_attribute("href")
                if not href.startswith("http"):
                    href = "https://www.tpu.ro" + href
                results.append({"title": title, "url": href})
            except Exception:
                continue

        return results

    def close(self):
        self.driver.quit()


def search_tpu(query: str, max_results: int = 5) -> list[dict]:
    """
    Convenience function: wraps TPUFinder so other modules can simply do:
        from forumuri.scraper_tpu import search_tpu
    """
    finder = TPUFinder()
    try:
        return finder.search(query, max_results)
    finally:
        finder.close()
