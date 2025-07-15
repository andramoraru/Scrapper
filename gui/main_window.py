from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from gui.products_page import ProductsPage
from gui.forums_page import ForumsPage

class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pricy App - Compara Preturi si Forumuri")
        self.resize(1000, 700)
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)

        self.products_page = ProductsPage(self.show_welcome_screen)
        self.forums_page = ForumsPage(self.show_welcome_screen)


        self.welcome_widget = self.create_welcome_screen()

        self.central.addWidget(self.welcome_widget)   # index 0
        self.central.addWidget(self.products_page)    # index 1
        self.central.addWidget(self.forums_page)      # index 2

    def show_welcome_screen(self):
        self.central.setCurrentIndex(0)

    def show_products_page(self):
        self.central.setCurrentIndex(1)

    def show_forums_page(self):
        self.central.setCurrentIndex(2)

    def create_welcome_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("assets/logo.png")
        pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Bine ai venit în aplicatia Pricy")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_products = QPushButton("Cauta produse si compara preturi")
        btn_products.setMinimumHeight(40)
        btn_products.clicked.connect(self.show_products_page)
        layout.addWidget(btn_products)

        btn_forums = QPushButton("Acceseaza forumuri (TPU, Stack Overflow)")
        btn_forums.setMinimumHeight(40)
        btn_forums.clicked.connect(self.show_forums_page)
        layout.addWidget(btn_forums)

        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #e3f2fd;")
        return widget
