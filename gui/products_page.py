import re
import sys
import requests
import requests_cache
from io import BytesIO
from urllib.parse import urlparse
from difflib import SequenceMatcher
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QHBoxLayout,QCompleter
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import json, os

requests_cache.install_cache('http_cache', expire_after=3600)

from scrapper_emag import search_emag_products
from scraper_cel import search_cel
from db_manager import (
    product_exists, get_last_price,
    insert_product, insert_price
)

HISTORY_FILE = "search_history.json"
MAX_HISTORY = 20


class ProductsPage(QWidget):
    MAX_RESULTS_PER_SITE = 10
    MATCH_THRESHOLD = 0.5

    def __init__(self, go_back_callback):
        super().__init__()
        self.go_back_callback = go_back_callback
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        if os.path.exists(HISTORY_FILE):
            history = json.load(open(HISTORY_FILE, 'r', encoding='utf-8'))
        else:
            history = []
        completer = QCompleter(history)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cauta produs (ex: iphone 13)...")
        self.search_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.search_input)

        btn_row = QHBoxLayout()
        self.search_btn = QPushButton("Cauta produs")
        self.search_btn.clicked.connect(self.search_products)
        btn_row.addWidget(self.search_btn)

        self.history_btn = QPushButton("Vezi istoric preturi")
        self.history_btn.clicked.connect(self.show_price_history)
        btn_row.addWidget(self.history_btn)

        layout.addLayout(btn_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_container.setLayout(self.result_layout)
        self.scroll.setWidget(self.result_container)
        layout.addWidget(self.scroll)

        self.back_btn = QPushButton("⬅ Înapoi la ecranul principal")
        self.back_btn.clicked.connect(self.go_back_callback)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #f1f8e9;")

    def clean_name(self, name):
        name = name.lower()
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", " ", name)
        remove_words = ['negru', 'alb', 'gri', 'cu tva', 'la reducere', 'în stoc']
        for w in remove_words:
            name = name.replace(w, '')
        return name.strip()

    def similar(self, a, b):
        return SequenceMatcher(None, self.clean_name(a), self.clean_name(b)).ratio()

    def find_matching_pairs(self, emag_list, cel_list, threshold=None):
        if threshold is None:
            threshold = self.MATCH_THRESHOLD
        pairs = []
        used_cel = set()
        for e in emag_list:
            best_score, best_idx = 0, -1
            for idx, c in enumerate(cel_list):
                if idx in used_cel:
                    continue
                score = self.similar(e['name'], c['name'])
                if score > best_score:
                    best_score, best_idx = score, idx
            if best_score >= threshold:
                pairs.append((e, cel_list[best_idx]))
                used_cel.add(best_idx)
        return pairs

    def save_query_to_history(self, query):
        if os.path.exists(HISTORY_FILE):
            history = json.load(open(HISTORY_FILE, 'r', encoding='utf-8'))
        else:
            history = []
        if query in history:
            history.remove(query)
        history.insert(0, query)
        history = history[:MAX_HISTORY]
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def search_products(self):
        query = self.search_input.text().strip()
        if not query:
            return

        for i in reversed(range(self.result_layout.count())):
            w = self.result_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        try:
            emag = search_emag_products(query, self.MAX_RESULTS_PER_SITE)
            cel = search_cel(query, self.MAX_RESULTS_PER_SITE)
        except TypeError:
            emag = search_emag_products(query)
            cel = search_cel(query)

        for p in emag: p['site'] = 'eMAG'
        for p in cel: p['site'] = 'CEL'

        pairs = self.find_matching_pairs(emag, cel)
        for e, c in pairs:
            self.add_comparison_card(e, c)

        for prod in emag + cel:
            color = '#c62828' if prod['site']=='eMAG' else '#1565c0'
            self.add_product_card(prod, color)

        for prod in emag + cel:
            url = prod['url']
            domain = urlparse(url).netloc
            if not product_exists(url):
                insert_product(prod['name'], domain, url)
                insert_price(url, prod['price'])
            else:
                last = get_last_price(url)
                if last is None or prod['price'] != last:
                    insert_price(url, prod['price'])

    def add_product_card(self, product, source_color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(
            "background-color: white; border:1px solid #ccc;"
            "border-radius:6px; padding:10px;"
        )
        layout = QHBoxLayout()
        image_label = QLabel(); image_label.setFixedSize(100,100)
        pix = QPixmap("assets/default_product.png")
        if product.get('image'):
            try:
                r = requests.get(product['image'], timeout=5)
                if r.status_code==200:
                    pix.loadFromData(r.content)
            except: pass
        pix = pix.scaled(100,100,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        image_label.setPixmap(pix)
        layout.addWidget(image_label)
        info = QVBoxLayout()
        title = QLabel(f"<b>{product['name']}</b>")
        title.setWordWrap(True); title.setFont(QFont("Arial",11))
        info.addWidget(title)
        price = QLabel(f"<span style='color:green;font-size:14px;'>{product['price']} RON</span>")
        info.addWidget(price)
        link = QLabel(f"<a href='{product['url']}'>{product['url']}</a>")
        link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link.setOpenExternalLinks(True)
        info.addWidget(link)
        src = QLabel(f"Sursa: <span style='color:{source_color}'>{product['site']}</span>")
        info.addWidget(src)
        layout.addLayout(info)
        card.setLayout(layout)
        self.result_layout.addWidget(card)

    def add_comparison_card(self, prod1, prod2):
        card = QFrame(); card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(
            "background-color:#e3f2fd; border:1px solid #90caf9;"
            "border-radius:6px; padding:10px;"
        )
        layout = QVBoxLayout()
        name = QLabel(f"<b>{prod1['name']}</b>"); name.setFont(QFont("Arial",11))
        btn = QPushButton("Compară prețuri")
        btn.setStyleSheet("background-color:#00796b;color:white;")
        btn.clicked.connect(lambda: self.open_comparison(prod1, prod2))
        layout.addWidget(name); layout.addWidget(btn)
        card.setLayout(layout)
        self.result_layout.addWidget(card)

    def open_comparison(self, prod1, prod2):
        from gui.price_comparison_window import PriceComparisonWindow
        self.compare_window = PriceComparisonWindow(prod1, prod2)
        self.compare_window.show()

    def show_price_history(self):
        from gui.price_history_window import PriceHistoryWindow
        self.history_window = PriceHistoryWindow()
        self.history_window.show()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = ProductsPage(lambda: app.quit())
    w.show()
    sys.exit(app.exec_())
