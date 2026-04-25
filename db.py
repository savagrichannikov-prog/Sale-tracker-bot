import sqlite3

DB_NAME = "data.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        articule TEXT NOT NULL,
        last_price INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def add_item(user_id, url, articule, price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO items (user_id, url, articule, last_price) VALUES (?, ?, ?, ?)",
        (user_id, url, articule, price)
    )

    conn.commit()
    conn.close()


def get_items(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, url, articule, last_price FROM items WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_items():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id, user_id, url, articule, last_price FROM items")
    rows = cur.fetchall()

    conn.close()
    return rows


def remove_item(user_id, item_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM items WHERE user_id = ? AND id = ?", (user_id, item_id))

    conn.commit()
    conn.close()


def update_price(item_id, new_price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("UPDATE items SET last_price = ? WHERE id = ?", (new_price, item_id))

    conn.commit()
    conn.close()
