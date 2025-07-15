from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config import get_connection

class PriceChartWindow(QWidget):
    def __init__(self, product_id, product_name):
        super().__init__()
        self.setWindowTitle(f"Evoluție preț: {product_name}")
        self.product_id = product_id
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.add_subplot(111)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot_graph()

    def plot_graph(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT price, timestamp FROM price_history WHERE product_id = ? ORDER BY timestamp", (self.product_id,))
        data = cursor.fetchall()
        conn.close()

        self.ax.clear()
        if data:
            prices, timestamps = zip(*data)
            self.ax.plot(timestamps, prices, marker='o')
            self.ax.set_title("Evoluție preț în timp")
            self.ax.set_xlabel("Dată")
            self.ax.set_ylabel("Preț (RON)")
            self.ax.tick_params(axis='x', rotation=45)
        else:
            self.ax.set_title("Fără date disponibile")
        self.canvas.draw()
