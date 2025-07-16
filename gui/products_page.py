from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from scrapper_emag import search_emag_products
from scraper_cel import search_cel
from db_manager import insert_product, insert_price
from urllib.parse import urlparse
import os
import requests
from io import BytesIO

class ProductsPage(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.go_back_callback = go_back_callback
        self.uploaded_image_path = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

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

    def normalize_name(self, name):
        return ''.join(c.lower() for c in name if c.isalnum())

    def search_products(self):
        query = self.search_input.text().strip()
        if not query:
            return

        for i in reversed(range(self.result_layout.count())):
            widget_to_remove = self.result_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        emag = search_emag_products(query)
        cel = search_cel(query)

        for p in emag:
            p["site"] = "eMAG"
        for p in cel:
            p["site"] = "CEL"

        normalized_emag = {self.normalize_name(p['name']): p for p in emag}
        normalized_cel = {self.normalize_name(p['name']): p for p in cel}

        all_keys = set(normalized_emag.keys()) | set(normalized_cel.keys())

        for key in all_keys:
            p_emag = normalized_emag.get(key)
            p_cel = normalized_cel.get(key)

            if p_emag and p_cel:
                self.add_comparison_card(p_emag, p_cel)
            elif p_emag:
                self.add_product_card(p_emag, "#c62828")
            elif p_cel:
                self.add_product_card(p_cel, "#1565c0")

            for p in filter(None, [p_emag, p_cel]):
                domain = urlparse(p['url']).netloc
                insert_product(p['name'], domain, p['url'])
                insert_price(p['url'], p['price'])

    def add_product_card(self, product, source_color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 6px; padding: 10px;")
        layout = QHBoxLayout()

        image_label = QLabel()
        image_label.setFixedSize(100, 100)

        pixmap = QPixmap("assets/default_product.png")
        if "image" in product and product["image"]:
            try:
                response = requests.get(product["image"], timeout=5)
                if response.status_code == 200:
                    img_data = response.content
                    pixmap.loadFromData(img_data)
            except Exception as e:
                print(f"Nu s-a putut încărca imaginea: {e}")

        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        layout.addWidget(image_label)

        info_layout = QVBoxLayout()

        title = QLabel(f"<b>{product['name']}</b>")
        title.setWordWrap(True)
        title.setFont(QFont("Arial", 11))
        info_layout.addWidget(title)

        price = QLabel(f"<span style='color: green; font-size: 14px;'>{product['price']} RON</span>")
        info_layout.addWidget(price)

        url = product['url']
        link = QLabel(f"<a href='{url}'>{url}</a>")
        link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link.setOpenExternalLinks(True)
        info_layout.addWidget(link)

        source = QLabel(f"Sursa: <span style='color:{source_color}'>{product['site']}</span>")
        info_layout.addWidget(source)

        layout.addLayout(info_layout)
        card.setLayout(layout)
        self.result_layout.addWidget(card)

    def add_comparison_card(self, prod1, prod2):
        from gui.price_comparison_window import PriceComparisonWindow
        card = QFrame()
        layout = QVBoxLayout()
        name_label = QLabel(f"<b>{prod1['name']}</b>")
        name_label.setFont(QFont("Arial", 11))
        compare_btn = QPushButton("Compara preturi")
        compare_btn.setStyleSheet("background-color: #00796b; color: white;")
        compare_btn.clicked.connect(lambda: self.open_comparison(prod1, prod2))

        layout.addWidget(name_label)
        layout.addWidget(compare_btn)
        card.setLayout(layout)
        card.setStyleSheet("background-color: #e3f2fd; border: 1px solid #90caf9; padding: 10px;")
        self.result_layout.addWidget(card)

    def open_comparison(self, prod1, prod2):
        from gui.price_comparison_window import PriceComparisonWindow
        self.compare_window = PriceComparisonWindow(prod1, prod2)
        self.compare_window.show()

    def show_price_history(self):
        from gui.price_history_window import PriceHistoryWindow
        self.history_window = PriceHistoryWindow()
        self.history_window.show()
