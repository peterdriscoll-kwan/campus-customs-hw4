"""Tools the Campus Customs chat agent can call.

Every tool reads straight from campus_customs.db (via db.py) so the agent's
answers about products, prices, and stock are grounded in the real catalogue
instead of the model's own guesses. Stock tools return a ready-to-use, honest
message (including an apology when something is out of stock) so the agent
relays facts instead of composing them from scratch.
"""
import re

from db import get_connection, get_product_row, inventory_for, serialize_product
from models import ProductInfo, ProductStock, ProductSummary, SizeStock, SizeStockCheck

_WORD_RE = re.compile(r"[a-z0-9]+")
_VALID_SIZES = {"XS", "S", "M", "L", "XL", "XXL"}


def _tokenize(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _searchable_text(row) -> str:
    return " ".join(
        [
            row["name"],
            row["garment_type"],
            row["description"],
            row["colors"],
            row["search_tags"],
        ]
    )


def search_products(query: str, limit: int = 8) -> list[ProductSummary]:
    """Search the Campus Customs catalogue for products matching a shopper's query.

    Matches against product name, garment type, description, colors, and search
    tags. Returns compact summaries (not full detail) ranked by relevance.
    Returns an empty list if nothing matches — that means the shop genuinely
    doesn't carry it, not that the search failed.

    Args:
        query: Shopper's search phrase, e.g. "navy hoodie" or "yale hockey gift".
        limit: Maximum number of results to return (default 8).
    """
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
        scored = []
        for row in rows:
            haystack_tokens = _tokenize(_searchable_text(row))
            overlap = len(query_tokens & haystack_tokens)
            if overlap == 0:
                continue
            scored.append((overlap, row))
        scored.sort(key=lambda pair: pair[0], reverse=True)

        results = []
        for _, row in scored[:limit]:
            product = serialize_product(conn, row)
            results.append(
                ProductSummary(
                    product_id=product["product_id"],
                    name=product["name"],
                    garment_type=product["garment_type"],
                    colors=product["colors"],
                    price=product["price"],
                    total_stock=product["total_stock"],
                )
            )
        return results
    finally:
        conn.close()


def get_product_info(product_id: str) -> ProductInfo | None:
    """Look up description and price for one product by its exact product_id.

    Use this for "what is it" / "how much is it" questions. For stock questions,
    use get_stock or check_size_stock instead. Returns None if the product_id
    doesn't exist in the catalogue — treat that as "not sold here", never guess.

    Args:
        product_id: The exact product_id, typically from a prior search_products result.
    """
    conn = get_connection()
    try:
        row = get_product_row(conn, product_id)
        if row is None:
            return None
        product = serialize_product(conn, row)
        return ProductInfo(
            product_id=product["product_id"],
            name=product["name"],
            garment_type=product["garment_type"],
            description=product["description"],
            colors=product["colors"],
            price=product["price"],
        )
    finally:
        conn.close()


def get_stock(product_id: str) -> ProductStock | None:
    """Look up stock for every size of one product, straight from the inventory table.

    Use this for "how many do you have" / "what sizes are in stock" questions
    covering a whole product. Returns None if the product_id doesn't exist.
    If every size is at 0, out_of_stock_note carries a ready-to-use apology —
    relay it honestly rather than hedging or omitting it.

    Args:
        product_id: The exact product_id to check.
    """
    conn = get_connection()
    try:
        row = get_product_row(conn, product_id)
        if row is None:
            return None
        name = row["name"]
        sizes = [SizeStock(size=s["size"], quantity=s["quantity"], in_stock=s["quantity"] > 0) for s in inventory_for(conn, product_id)]
        total = sum(s.quantity for s in sizes)
        note = None
        if total == 0:
            note = f"I'm sorry, but the {name} is currently out of stock in every size."
        return ProductStock(product_id=product_id, name=name, sizes=sizes, total_stock=total, out_of_stock_note=note)
    finally:
        conn.close()


def find_alternatives(product_id: str, limit: int = 4) -> list[ProductSummary]:
    """Find real, currently-in-stock products similar to one that's out of stock.

    Use this whenever get_stock or check_size_stock reports 0 quantity, so you
    can offer the shopper a genuine alternative instead of just an apology.
    Matches by garment type, color, and search tags against the source product;
    only returns products with total_stock > 0, and never includes the source
    product itself. Returns an empty list if nothing similar is in stock —
    in that case, don't invent a substitute, just apologize.

    Args:
        product_id: The out-of-stock product's exact product_id.
        limit: Maximum number of alternatives to return (default 4).
    """
    conn = get_connection()
    try:
        source_row = get_product_row(conn, product_id)
        if source_row is None:
            return []
        source_tokens = _tokenize(_searchable_text(source_row))

        rows = conn.execute("SELECT * FROM catalogue WHERE product_id != ?", (product_id,)).fetchall()
        scored = []
        for row in rows:
            product = serialize_product(conn, row)
            if product["total_stock"] <= 0:
                continue
            garment_match = 2 if row["garment_type"] == source_row["garment_type"] else 0
            tag_overlap = len(source_tokens & _tokenize(_searchable_text(row)))
            score = garment_match + tag_overlap
            if score == 0:
                continue
            scored.append((score, product))
        scored.sort(key=lambda pair: pair[0], reverse=True)

        return [
            ProductSummary(
                product_id=product["product_id"],
                name=product["name"],
                garment_type=product["garment_type"],
                colors=product["colors"],
                price=product["price"],
                total_stock=product["total_stock"],
            )
            for _, product in scored[:limit]
        ]
    finally:
        conn.close()


def check_size_stock(product_id: str, size: str) -> SizeStockCheck | None:
    """Check exact stock quantity for one product in one specific size.

    Use this when the shopper names a specific size. Returns None if the
    product_id doesn't exist in the catalogue at all.

    Args:
        product_id: The exact product_id to check.
        size: One of XS, S, M, L, XL, XXL.
    """
    conn = get_connection()
    try:
        row = get_product_row(conn, product_id)
        if row is None:
            return None
        name = row["name"]
        normalized_size = size.upper().strip()

        stock_row = conn.execute(
            "SELECT quantity FROM inventory WHERE product_id = ? AND size = ?",
            (product_id, normalized_size),
        ).fetchone()
        quantity = stock_row["quantity"] if stock_row else 0
        in_stock = quantity > 0

        if normalized_size not in _VALID_SIZES:
            note = f"'{size}' isn't one of our sizes (XS, S, M, L, XL, XXL) for the {name}."
        elif in_stock:
            note = f"Yes — the {name} has {quantity} left in size {normalized_size}."
        else:
            note = f"I'm sorry, but the {name} is currently out of stock in size {normalized_size}."

        return SizeStockCheck(
            product_id=product_id,
            name=name,
            size=normalized_size,
            quantity=quantity,
            in_stock=in_stock,
            note=note,
        )
    finally:
        conn.close()
