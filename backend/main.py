"""Campus Customs API: FastAPI app serving the product catalogue/images, account
auth, and the PydanticAI chat agent (agent.py + tools.py + prompts/prompt.md).

Run from this folder with: uvicorn main:app --reload --port 8000
"""
import logging
import re
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import DEFAULT_MODEL, SMART_MODEL, ChatDeps, run_chat, wants_smart_model
from auth import hash_password, verify_password
from db import (
    PRODUCTS_DIR,
    get_chat_history,
    get_connection,
    get_product_row,
    get_user_row,
    insert_chat_message,
    serialize_product,
)
from guardrails import build_retry_message, find_price_mismatches
from models import ChatHistoryEntry, ChatResponse, PageContext, ProductCardOut, ProductInfo, PublicUser

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")


@app.get("/api/products")
def list_products():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        return [serialize_product(conn, row) for row in rows]
    finally:
        conn.close()


@app.get("/api/products/{product_id}")
def get_product_detail(product_id: str):
    conn = get_connection()
    try:
        row = get_product_row(conn, product_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return serialize_product(conn, row)
    finally:
        conn.close()


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=200)


def _public_user(row: sqlite3.Row) -> PublicUser:
    return PublicUser(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        name=row["name"],
        email=row["email"],
    )


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterRequest):
    email = payload.email.strip().lower()
    if not EMAIL_PATTERN.match(email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")

    first_name = payload.first_name.strip()
    last_name = payload.last_name.strip()
    full_name = f"{first_name} {last_name}".strip()
    password_hash = hash_password(payload.password)

    conn = get_connection()
    try:
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) "
                "VALUES (?, ?, ?, ?, ?)",
                (full_name, email, password_hash, first_name, last_name),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="An account with that email already exists")

        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _public_user(row)
    finally:
        conn.close()


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    email = payload.email.strip().lower()
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        # Same generic error whether the email is unknown or the password is wrong,
        # so a login attempt can't be used to discover which emails have accounts.
        if row is None or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return _public_user(row)
    finally:
        conn.close()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    user_id: int | None = Field(
        default=None,
        description="Logged-in shopper's user id. Omit/None for guests — guest chats are never persisted.",
    )
    page_context: PageContext | None = None
    use_smart_model: bool = Field(
        default=False,
        description=(
            "Explicit override to force gpt-6-astra. Normally left False — the shopper's "
            "message is scanned for a plain-language request instead (see wants_smart_model)."
        ),
    )


def _resolve_products(conn, product_ids: list[str]) -> list[ProductCardOut]:
    products: list[ProductCardOut] = []
    for product_id in product_ids:
        row = get_product_row(conn, product_id)
        if row is None:
            # The agent named a product_id that isn't in the catalogue (it
            # shouldn't, per the system prompt) — drop it instead of trusting
            # a possibly-hallucinated id, rather than surfacing broken data.
            continue
        products.append(ProductCardOut(**serialize_product(conn, row)))
    return products


@app.get("/api/chat/history/{user_id}", response_model=list[ChatHistoryEntry])
def chat_history(user_id: int):
    conn = get_connection()
    try:
        if get_user_row(conn, user_id) is None:
            raise HTTPException(status_code=404, detail="User not found")
        return get_chat_history(conn, user_id)
    finally:
        conn.close()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    conn = get_connection()
    try:
        user_row = get_user_row(conn, payload.user_id) if payload.user_id is not None else None
        escalate = payload.use_smart_model or wants_smart_model(payload.message)
        deps = ChatDeps(user=_public_user(user_row) if user_row is not None else None, escalated=escalate)
        model_name = SMART_MODEL if escalate else DEFAULT_MODEL

        if payload.page_context and payload.page_context.current_product_id:
            product_row = get_product_row(conn, payload.page_context.current_product_id)
            if product_row is not None:
                product = serialize_product(conn, product_row)
                deps.current_product = ProductInfo(
                    product_id=product["product_id"],
                    name=product["name"],
                    garment_type=product["garment_type"],
                    description=product["description"],
                    colors=product["colors"],
                    price=product["price"],
                )

        # Persist the shopper's message before calling the model, so a chat that
        # errors out still leaves a record of what was asked.
        if user_row is not None:
            insert_chat_message(conn, payload.user_id, "user", payload.message)

        try:
            agent_reply = await run_chat(payload.message, deps=deps, model_name=model_name)
        except Exception:
            # Covers upstream model/content-filter errors (e.g. Portkey/Azure rejecting
            # a jailbreak-style message) and any other agent failure. Never leak
            # exception internals to the client; log server-side for debugging.
            logging.exception("Chat agent run failed")
            fallback = "Sorry, I couldn't process that message. Try rephrasing your question about our products."
            if user_row is not None:
                insert_chat_message(conn, payload.user_id, "assistant", fallback)
            return ChatResponse(reply=fallback, products=[], model_used=model_name)

        products = _resolve_products(conn, agent_reply.product_ids)

        # Price-accuracy guardrail (Problem 9): if the reply states a dollar amount
        # that doesn't match any resolved product's real price, don't trust it —
        # retry once with a corrective nudge before ever showing it to the shopper.
        mismatches = find_price_mismatches(agent_reply.reply, products)
        if mismatches:
            logging.warning("Price guardrail triggered: reply mentioned unmatched price(s) %s", mismatches)
            retry_message = build_retry_message(payload.message, mismatches)
            try:
                retry_reply = await run_chat(retry_message, deps=deps, model_name=model_name)
                retry_products = _resolve_products(conn, retry_reply.product_ids)
                if not find_price_mismatches(retry_reply.reply, retry_products):
                    agent_reply, products = retry_reply, retry_products
                else:
                    logging.warning("Price guardrail retry still mismatched — falling back to a safe reply")
                    agent_reply.reply = (
                        "Sorry, I want to double-check that price before I quote it — could you ask again in a moment?"
                    )
                    agent_reply.product_ids = []
                    products = []
            except Exception:
                logging.exception("Price guardrail retry failed")

        if user_row is not None:
            insert_chat_message(
                conn,
                payload.user_id,
                "assistant",
                agent_reply.reply,
                products=[p.model_dump() for p in products],
            )

        return ChatResponse(reply=agent_reply.reply, products=products, model_used=model_name)
    finally:
        conn.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
