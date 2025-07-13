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

def insert_price(url, price):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM products WHERE url = ?", url)
        row = cursor.fetchone()
        if row:
            product_id = row[0]
            cursor.execute("""
                INSERT INTO price_history (product_id, price) VALUES (?, ?)
            """, product_id, price)
            conn.commit()
    finally:
        conn.close()
