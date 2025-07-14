from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QScrollArea, QFrame, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from scrapper_emag import search_emag_products
from scraper_cel import search_cel
from db_manager import insert_product, insert_price
from gui.price_history_window import PriceHistoryWindow
from urllib.parse import urlparse

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Tracker - Compara Preturi")
        self.resize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Cauta produs (ex: iphone 13)...")
        self.input.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.input)

        self.search_btn = QPushButton("Cauta produs")
        self.search_btn.clicked.connect(self.search_products)
        self.layout.addWidget(self.search_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_container.setLayout(self.result_layout)
        self.scroll.setWidget(self.result_container)
        self.layout.addWidget(self.scroll)

        self.btn_view_history = QPushButton("Vezi istoric preturi")
        self.btn_view_history.clicked.connect(self.show_price_history)
        self.layout.addWidget(self.btn_view_history)

        self.setLayout(self.layout)

    def add_product_card(self, product, source_color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: #f7f7f7; border: 1px solid #ccc; border-radius: 6px; padding: 10px;")
        layout = QVBoxLayout()

        title = QLabel(f"<b>{product['name']}</b>")
        title.setWordWrap(True)
        title.setFont(QFont("Arial", 11))
        layout.addWidget(title)

        price = QLabel(f"<span style='color: green; font-size: 14px;'>{product['price']} RON</span>")
        layout.addWidget(price)

        url = product['url']
        link = QLabel(f"<a href='{url}'>{url}</a>")
        link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link.setOpenExternalLinks(True)
        layout.addWidget(link)

        source = QLabel(f"Sursa: <span style='color:{source_color}'>{product['site']}</span>")
        layout.addWidget(source)

        card.setLayout(layout)
        self.result_layout.addWidget(card)

    def search_products(self):
        query = self.input.text().strip()
        if not query:
            QMessageBox.warning(self, "Eroare", "Te rog introdu un produs.")
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

        if not products:
            warning = QLabel("Niciun produs gasit.")
            self.result_layout.addWidget(warning)
            return

        for p in products:
            domain = urlparse(p['url']).netloc
            insert_product(p['name'], domain, p['url'])
            insert_price(p['url'], p['price'])

    def show_price_history(self):
        self.history_window = PriceHistoryWindow()
        self.history_window.show()
