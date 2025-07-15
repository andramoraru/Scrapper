from config import get_connection

def insert_product(name, site, url):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM products WHERE url = ?)
                INSERT INTO products (name, site, url) VALUES (?, ?, ?)
        """, url, name, site, url)
        conn.commit()
    finally:
        conn.close()

def insert_price(url, new_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 1 ph.price
        FROM price_history ph
        JOIN products p ON p.id = ph.product_id
        WHERE p.url = ?
        ORDER BY ph.timestamp DESC
    """, (url,))
    row = cursor.fetchone()
    if row and row[0] == new_price:
        conn.close()
        return  #salvez numai pentru un nou pret in baza de date, astfel se salveaza numai la schimbari

    cursor.execute("SELECT id FROM products WHERE url = ?", (url,))
    product = cursor.fetchone()
    if product:
        cursor.execute("INSERT INTO price_history (product_id, price, timestamp) VALUES (?, ?, GETDATE())",
                       (product[0], new_price))
        conn.commit()

    conn.close()
