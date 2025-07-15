from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from gui.price_chart_window import PriceChartWindow
from config import get_connection
import csv
from collections import defaultdict
from gui.price_comparison_window import PriceComparisonWindow

class PriceHistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Istoric Preturi")
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtreaza dupa nume produs...")
        layout.addWidget(self.filter_input)

        self.sort_box = QComboBox()
        self.sort_box.addItems([
            "Sortare: Implicita",
            "Pret crescator",
            "Pret descrescator",
            "Cele mai recente"
        ])
        layout.addWidget(self.sort_box)

        self.refresh_btn = QPushButton("Reincarca")
        self.refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("Exporta în CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(self.export_btn)

        self.output = QTextBrowser()
        self.output.setOpenExternalLinks(False)
        self.output.anchorClicked.connect(self.handle_anchor_click)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.load_data()

    def normalize_url(self, url: str) -> str:
        if url.startswith("http://http") or url.startswith("https://https"):
            return url[url.find("http", 1):]
        elif url.startswith("http://") or url.startswith("https://"):
            return url
        else:
            return "https://" + url

    def load_data(self):
        self.output.clear()
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT p.id, p.name, p.site, p.url, ph.price, ph.timestamp
            FROM products p
            JOIN price_history ph ON p.id = ph.product_id
        """
        params = []

        if text := self.filter_input.text().strip():
            query += " WHERE p.name LIKE ?"
            params.append(f"%{text}%")

        order = self.sort_box.currentText()
        if order == "Pret crescator":
            query += " ORDER BY ph.price ASC"
        elif order == "Pret descrescator":
            query += " ORDER BY ph.price DESC"
        elif order == "Cele mai recente":
            query += " ORDER BY ph.timestamp DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        grouped = defaultdict(list)
        for prod_id, name, site, url, price, ts in rows:
            grouped[(prod_id, name, site)].append((price, ts, url))

        html_parts = []
        for (prod_id, name, site), entries in grouped.items():
            html_parts.append(f"<b>{name} | {site}</b><br>")
            for price, ts, url in entries:
                url = self.normalize_url(url)
                html_parts.append(f" - {price:.2f} RON la {ts.strftime('%d.%m.%Y %H:%M')}<br>")
                html_parts.append(f"<a href='{url}'>{url}</a><br>")
            html_parts.append(
                f"<a href='chart:///{prod_id}|{name}' "
                "style='font-weight:bold; color:#222; text-decoration:underline;'>"
                " Vezi grafic</a><br>"
                f"<a href='compare:///{prod_id}|{name}' "
                "style='font-weight:bold; color:#00695c; text-decoration:underline;'>"
                " Compara preturi</a><br><hr>"
            )

        self.output.setHtml("".join(html_parts))

    def handle_anchor_click(self, url: QUrl):
        if url.scheme() == "chart":
            data = url.path().lstrip("/")
            try:
                prod_id_str, name = data.split("|", 1)
                prod_id = int(prod_id_str)
                self.chart_window = PriceChartWindow(prod_id, name)
                self.chart_window.showMaximized()
            except Exception:
                return

        elif url.scheme() == "compare":
            data = url.path().lstrip("/")
            try:
                prod_id_str, name = data.split("|", 1)
                prod_id = int(prod_id_str)
                self.compare_window = PriceComparisonWindow(name)
                self.compare_window.show()
            except Exception:
                return

        else:
            QDesktopServices.openUrl(url)

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporta ca CSV", "istoric.csv", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.site, p.url, ph.price, ph.timestamp
            FROM products p
            JOIN price_history ph ON p.id = ph.product_id
        """)
        rows = cursor.fetchall()
        conn.close()

        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Produs", "Site", "Link", "Pret", "Data"])
            for name, site, url, price, ts in rows:
                writer.writerow([
                    name,
                    site,
                    self.normalize_url(url),
                    f"{price:.2f}",
                    ts.strftime('%Y-%m-%d %H:%M:%S')
                ])
