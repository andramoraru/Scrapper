
from config import get_connection


def insert_product(name, site, url):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "IF NOT EXISTS (SELECT 1 FROM products WHERE url = ?)\n"
            "    INSERT INTO products (name, site, url) VALUES (?, ?, ?)",
            (url, name, site, url)
        )
        conn.commit()
    finally:
        conn.close()


def insert_price(url, new_price):
    conn = get_connection()
    cursor = conn.cursor()
    try:
       
        cursor.execute(
            "SELECT TOP 1 ph.price "
            "FROM price_history ph "
            "JOIN products p ON p.id = ph.product_id "
            "WHERE p.url = ? "
            "ORDER BY ph.timestamp DESC", 
            (url,)
        )
        row = cursor.fetchone()
        if row and row[0] == new_price:
            return  

        # Obtine product_id
        cursor.execute("SELECT id FROM products WHERE url = ?", (url,))
        prod = cursor.fetchone()
        if prod:
            product_id = prod[0]
            cursor.execute(
                "INSERT INTO price_history (product_id, price, timestamp) VALUES (?, ?, GETDATE())",
                (product_id, new_price)
            )
            conn.commit()
    finally:
        conn.close()


def product_exists(url):
  
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM products WHERE url = ?", (url,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def get_last_price(url):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT TOP 1 ph.price "
            "FROM price_history ph "
            "JOIN products p ON p.id = ph.product_id "
            "WHERE p.url = ? "
            "ORDER BY ph.timestamp DESC", 
            (url,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()
