from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from config import get_connection
import csv

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
        self.sort_box.addItems(["Sortare: Implicita", "Pret crescator", "Pret descrescator", "Cele mai recente"])
        layout.addWidget(self.sort_box)

        self.refresh_btn = QPushButton("Reincarca")
        self.refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("Exporta în CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(self.export_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.output.clear()
        conn = get_connection()
        cursor = conn.cursor()

        base_query = """
            SELECT p.name, p.site, p.url, ph.price, ph.timestamp
            FROM products p
            JOIN price_history ph ON p.id = ph.product_id
        """

        conditions = []
        params = []

        if self.filter_input.text().strip():
            conditions.append("p.name LIKE ?")
            params.append(f"%{self.filter_input.text().strip()}%")

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        order_clause = self.sort_box.currentText()
        if order_clause == "Preț crescator":
            base_query += " ORDER BY ph.price ASC"
        elif order_clause == "Preț descrescator":
            base_query += " ORDER BY ph.price DESC"
        elif order_clause == "Cele mai recente":
            base_query += " ORDER BY ph.timestamp DESC"

        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        conn.close()

        grouped = {}
        for name, site, url, price, timestamp in rows:
            key = f"{name} | {site}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append((price, timestamp, url))

        for key, entries in grouped.items():
            self.output.append(f"<b>{key}</b>")
            for price, ts, url in entries:
                self.output.append(f" - {price:.2f} RON la {ts.strftime('%d.%m.%Y %H:%M')}<br><a href='{url}'>{url}</a>")
            self.output.append("<hr>")

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportă ca CSV", "istoric.csv", "CSV Files (*.csv)")
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
                writer.writerow([name, site, url, price, ts.strftime('%Y-%m-%d %H:%M:%S')])
