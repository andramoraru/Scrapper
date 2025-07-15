from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextBrowser, QHBoxLayout, QLineEdit, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from forumuri.scraper_tpu import search_tpu
from forumuri.scraper_stackOverflow import search_stackoverflow_duckduckgo

class ForumsPage(QWidget):
    def __init__(self,go_back_callback):
        super().__init__()
        self.go_back_callback = go_back_callback
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.title = QLabel("Cauta intrebari pe forumuri")
        self.title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.title)

        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Introduceti subiectul cautarii (ex: python)")
        input_layout.addWidget(self.input)

        self.btn_tpu = QPushButton("Cauta pe TPU")
        self.btn_tpu.clicked.connect(self.search_tpu)
        input_layout.addWidget(self.btn_tpu)

        self.btn_so = QPushButton("Cauta pe Stack Overflow")
        self.btn_so.clicked.connect(self.search_stackoverflow)
        input_layout.addWidget(self.btn_so)
        self.back_btn = QPushButton("⬅ Înapoi la ecranul principal")
        self.back_btn.clicked.connect(self.go_back_callback)
        layout.addWidget(self.back_btn)

        layout.addLayout(input_layout)

        self.results = QTextBrowser()
        self.results.setOpenExternalLinks(True)
        self.results.setOpenExternalLinks(True)
        layout.addWidget(self.results)


        self.setLayout(layout)
        self.setStyleSheet("background-color: #fff3e0;")

    def search_tpu(self):
        query = self.input.text().strip()
        if not query:
            return
        self.results.clear()
        results = search_tpu(query)
        if not results:
            self.results.setText("Niciun rezultat găsit pe TPU.")
            return
        for r in results:
            self.results.append(f" <b>{r['title']}</b>\n<a href='{r['url']}'>{r['url']}</a>\n")

    def search_stackoverflow(self):
        query = self.input.text().strip()
        if not query:
            return
        self.results.clear()
        results = search_stackoverflow_duckduckgo(query)
        if not results:
            self.results.setText(" Niciun rezultat gasit pe Stack Overflow.")
            return
        for r in results:
            self.results.append(f"🔹 <b>{r['title']}</b>\n<a href='{r['url']}'>{r['url']}</a>\n")
