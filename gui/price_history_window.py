from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from db_manager import get_connection

class PriceHistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Istoric Preturi")
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.name, p.site, h.price, h.timestamp
            FROM price_history h
            JOIN products p ON p.id = h.product_id
            ORDER BY p.name, p.site, h.timestamp DESC
        """)
        data = cursor.fetchall()
        conn.close()

        grouped = {}
        for name, site, price, timestamp in data:
            if name not in grouped:
                grouped[name] = {}
            if site not in grouped[name]:
                grouped[name][site] = []
            grouped[name][site].append((price, timestamp))

        for product, sites in grouped.items():
            header = QLabel(f" {product}")
            header.setFont(QFont("Arial", 14, QFont.Bold))
            content_layout.addWidget(header)

            for site, entries in sites.items():
                site_label = QLabel(f" {site}")
                site_label.setStyleSheet("color: #1565c0;" if "cel" in site.lower() else "color: #c62828;")
                site_label.setFont(QFont("Arial", 11, QFont.Bold))
                content_layout.addWidget(site_label)

                for price, timestamp in entries:
                    time_str = timestamp.strftime("%d.%m.%y %H:%M")
                    line = QLabel(f"    {price} RON    {time_str}")
                    content_layout.addWidget(line)

            content_layout.addWidget(QFrame(frameShape=QFrame.HLine))
