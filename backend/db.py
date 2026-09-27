"""Shared SQLite access for the Campus Customs catalogue/inventory.

Used by both main.py (REST endpoints) and tools.py (agent tools) so there is
exactly one place that knows how to read the database.
"""
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "campus_customs.db"
PRODUCTS_DIR = BASE_DIR / "data" / "products"

_SIZE_ORDER = "CASE size WHEN 'XS' THEN 1 WHEN 'S' THEN 2 WHEN 'M' THEN 3 WHEN 'L' THEN 4 WHEN 'XL' THEN 5 WHEN 'XXL' THEN 6 ELSE 7 END"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inventory_for(conn: sqlite3.Connection, product_id: str) -> list[dict]:
    rows = conn.execute(
        f"SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY {_SIZE_ORDER}",
        (product_id,),
    ).fetchall()
    return [{"size": r["size"], "quantity": r["quantity"]} for r in rows]


def serialize_product(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    inventory = inventory_for(conn, row["product_id"])
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_url": f"/media/{row['image_file_path']}",
        "price": row["price"],
        "inventory": inventory,
        "total_stock": sum(item["quantity"] for item in inventory),
    }


def get_product_row(conn: sqlite3.Connection, product_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
    ).fetchone()


def get_user_row(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def insert_chat_message(
    conn: sqlite3.Connection,
    user_id: int,
    role: str,
    content: str,
    products: list[dict] | None = None,
) -> None:
    conn.execute(
        "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
        (user_id, role, content, json.dumps(products) if products else None),
    )
    conn.commit()


def get_chat_history(conn: sqlite3.Connection, user_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT role, content, products_json, created_at FROM chat_messages "
        "WHERE user_id = ? ORDER BY id",
        (user_id,),
    ).fetchall()
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "products": json.loads(row["products_json"]) if row["products_json"] else [],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
