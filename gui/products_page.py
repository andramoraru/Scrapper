from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from scrapper_emag import search_emag_products
from scraper_cel import search_cel
from db_manager import insert_product, insert_price
from urllib.parse import urlparse
import os

class ProductsPage(QWidget):
    def __init__(self,go_back_callback):
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
        layout.addWidget(self.history_btn)


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

   

    def add_product_card(self, product, source_color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 6px; padding: 10px;")
        layout = QHBoxLayout()

        image_label = QLabel()
        pixmap = QPixmap("assets/default_product.png")
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

    def search_products(self):
        query = self.search_input.text().strip()
        if not query:
            return

        for i in reversed(range(self.result_layout.count())):
            widget_to_remove = self.result_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        products = []

        emag = search_emag_products(query)
        for p in emag:
            p["site"] = "eMAG"
            products.append(p)
            self.add_product_card(p, "#c62828")  # rosu

        cel = search_cel(query)
        for p in cel:
            p["site"] = "CEL"
            products.append(p)
            self.add_product_card(p, "#1565c0")  # albastru

        for p in products:
            domain = urlparse(p['url']).netloc
            insert_product(p['name'], domain, p['url'])
            insert_price(p['url'], p['price'])
            
    def show_price_history(self):
         from gui.price_history_window import PriceHistoryWindow
         self.history_window = PriceHistoryWindow()
         self.history_window.show()
