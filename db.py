import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    url TEXT,
    articule TEXT,
    last_price INTEGER
)
""")
conn.commit()


def add_item(user_id, url, articule, price):
    cur.execute("INSERT INTO items (user_id, url, articule, last_price) VALUES (?, ?, ?, ?)",
                (user_id, url, articule, price))
    conn.commit()


def get_items(user_id):
    cur.execute("SELECT id, url, articule, last_price FROM items WHERE user_id = ?", (user_id,))
    return cur.fetchall()


def remove_item(user_id, item_id):
    cur.execute("DELETE FROM items WHERE user_id = ? AND id = ?", (user_id, item_id))
    conn.commit()


def update_price(item_id, new_price):
    cur.execute("UPDATE items SET last_price = ? WHERE id = ?", (new_price, item_id))
    conn.commit()
  
