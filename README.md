# Scrapper
Proiect practica
ProductTracker este o aplicatie desktop scrisa in Python si PyQt5 pentru price tracking si comparare de produse intre mai multi retaileri online(eMAG, CEL). Scopul sau este de a gasi rapid produse, a compara preturi si a salva istoricul modificarilor in baza de date. 

Principalele functionalitati:
-Cautare simultana si comparare preturi pe eMAG, CEL
-Scraping inteligent cu Request si BeautifulSoup, Selenium headless
-Fereastra de comparatie vizuala si economii intr-un tabel interactiv
-Istoric de preturi salvat doar la modificari, cu vizualizare grafica
-Filtrare, sortare si export CSV din interfata de istoric
-Interogare forumuri TPU si StackOverflow direct din aplicatie

Folderul principal Scraper contine:
-config.py: functia get_connection() pentru SQL Server
-db_manager.py: functii insert_product, insert_price, product_exists, get_last_price
-scrappers: modulele scrapper_emag.py, scraper_cel.py
-forumuri: scraper_tpu.py, scraper_stackOverflow.y
-gui: fisierele products_page, forums_page, main_window, price_chart_window,price_comparison_window

Interfata de istoric permite filtrare dupa nume produs si sortare dupa data. Datele sunt grupate pe produs si afisate in QTextBrowser cu linkuri speciale pentru grafic. 
Export CSV genereaza un fisier UTF-8, cu antetul Produs, Site, Link, Pret, Data si toate randurile din price_history.
