from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from config import get_connection

class PriceComparisonWindow(QWidget):
    def __init__(self, product_name: str):
        super().__init__()
        self.product_name = product_name
        self.setWindowTitle(f"Compară prețuri • {product_name}")
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<h2>{self.product_name}</h2>"))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.site, ph.price, ph.timestamp
            FROM products p
            JOIN price_history ph ON p.id = ph.product_id
            WHERE p.name = ?
            ORDER BY ph.timestamp DESC
        """, (self.product_name,))
        rows = cur.fetchall()
        conn.close()

        
        latest = {}
        for site, price, ts in rows:
            if site not in latest:
                latest[site] = (price, ts)

        if not latest:
            layout.addWidget(QLabel(" Nu exista suficiente date pentru comparatie."))
            return

       
        cheapest_site, (cheapest_price, _) = min(latest.items(), key=lambda kv: kv[1][0])

       
        table = QTableWidget(len(latest), 5)
        table.setHorizontalHeaderLabels(["Site", "Pret curent", "Economii (RON)", "Economii (%)", "🏅"])

        for i, (site, (price, ts)) in enumerate(latest.items()):
            diff = price - cheapest_price
            pct = (diff / price * 100) if price else 0

            table.setItem(i, 0, QTableWidgetItem(site))
            table.setItem(i, 1, QTableWidgetItem(f"{price:.2f} RON"))
            table.setItem(i, 2, QTableWidgetItem(f"-{diff:.2f}"))
            table.setItem(i, 3, QTableWidgetItem(f"{pct:.1f}%"))
            table.setItem(i, 4, QTableWidgetItem("" if site == cheapest_site else ""))

        table.resizeColumnsToContents()
        layout.addWidget(table)
