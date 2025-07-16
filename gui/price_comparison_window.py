from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QUrl
import requests
from io import BytesIO
import webbrowser

class PriceComparisonWindow(QWidget):
    def __init__(self, product_emag: dict, product_cel: dict):
        super().__init__()
        self.product_emag = product_emag
        self.product_cel = product_cel
        self.setWindowTitle(f"Compară prețuri • {product_emag['name']}")
        self.resize(700, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

      
        title = QLabel(f"<h2>{self.product_emag['name']}</h2>")
        layout.addWidget(title)

     
        images_row = QHBoxLayout()

        for product in [self.product_emag, self.product_cel]:
            col = QVBoxLayout()
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap("assets/default_product.png")

            if product.get("image"):
                try:
                    response = requests.get(product["image"], timeout=5)
                    if response.status_code == 200:
                        pixmap.loadFromData(response.content)
                except Exception:
                    pass

            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
            col.addWidget(image_label)

            btn = QPushButton(f"Deschide pe {product['site']}")
            btn.clicked.connect(lambda _, link=product["url"]: webbrowser.open(link))
            col.addWidget(btn)
            images_row.addLayout(col)

        layout.addLayout(images_row)

     
        price1 = self.product_emag["price"]
        price2 = self.product_cel["price"]
        products_sorted = sorted(
            [self.product_emag, self.product_cel],
            key=lambda p: p['price']
        )
        cheapest = products_sorted[0]
        expensive = products_sorted[1]
        diff = expensive["price"] - cheapest["price"]
        pct = (diff / cheapest["price"]) * 100 if cheapest["price"] else 0

        table = QTableWidget(2, 5)
        table.setHorizontalHeaderLabels([
            "Site", "Pret", "Cel mai ieftin?", "Economisesti", "🏅"
        ])

        products = [self.product_emag, self.product_cel]
        prices = [p["price"] for p in products]
        cheapest_index = 0 if prices[0] <= prices[1] else 1
        expensive_index = 1 - cheapest_index
        savings_value = prices[expensive_index] - prices[cheapest_index]

        for i, product in enumerate(products):
            site = product["site"]
            price = product["price"]
            is_cheapest = i == cheapest_index

            table.setItem(i, 0, QTableWidgetItem(site))
            table.setItem(i, 1, QTableWidgetItem(f"{price:.2f} RON"))
            table.setItem(i, 2, QTableWidgetItem("✅" if is_cheapest else "❌"))

            if is_cheapest:
                table.setItem(i, 3, QTableWidgetItem(f"{savings_value:.2f} RON"))
                table.setItem(i, 4, QTableWidgetItem("🥇"))
            else:
                table.setItem(i, 3, QTableWidgetItem("-"))
                table.setItem(i, 4, QTableWidgetItem("🥈"))

        table.resizeColumnsToContents()
        layout.addWidget(table)





        table.resizeColumnsToContents()
        layout.addWidget(table)
