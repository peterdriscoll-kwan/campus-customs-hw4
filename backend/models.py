"""PydanticAI structured types for the Campus Customs chat agent."""
from datetime import datetime

from pydantic import BaseModel, Field


class ChatAgentReply(BaseModel):
    """The agent's structured output for one chat turn."""

    reply: str = Field(description="The assistant's reply to show the shopper, in Campus Customs voice.")
    product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Product IDs (from tool results only) to render as live product cards on the "
            "website — the API contract between this agent and the frontend's dynamic product "
            "panel. Most relevant first; for a browse/category question, include several (not "
            "just one). Leave empty if no specific products apply. Never invent an ID that "
            "wasn't returned by a tool call."
        ),
    )


class ProductSummary(BaseModel):
    """Compact search result — enough to help a shopper pick a product to ask more about."""

    product_id: str
    name: str
    garment_type: str
    colors: list[str]
    price: float = Field(description="Real db price in USD.")
    total_stock: int = Field(description="Units in stock across all sizes, straight from the inventory table.")


class ProductInfo(BaseModel):
    """Descriptive/price facts for one product — no stock detail (see ProductStock)."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float = Field(description="Real db price in USD; never estimate or round this.")


class SizeStock(BaseModel):
    """Stock for one size of one product."""

    size: str
    quantity: int
    in_stock: bool = Field(description="True if quantity > 0.")


class ProductStock(BaseModel):
    """Full per-size stock breakdown for one product, plus an honest overall note."""

    product_id: str
    name: str
    sizes: list[SizeStock]
    total_stock: int
    out_of_stock_note: str | None = Field(
        default=None,
        description=(
            "Set only when total_stock is 0: a ready-to-use apology sentence stating the "
            "product is out of stock in every size. The agent should relay this honestly, "
            "not soften or omit it."
        ),
    )


class SizeStockCheck(BaseModel):
    """Result of checking one specific size for one product."""

    product_id: str
    name: str
    size: str
    quantity: int
    in_stock: bool
    note: str = Field(
        description=(
            "Ready-to-use sentence for the shopper: an honest apology naming the product and "
            "size if quantity is 0, otherwise a short in-stock confirmation with the quantity."
        )
    )


class PublicUser(BaseModel):
    """Account fields safe to hand to the agent or return over the API — never password_hash."""

    id: int
    first_name: str
    last_name: str
    name: str
    email: str


class PageContext(BaseModel):
    """What the shopper is currently looking at in the frontend, sent with each chat turn."""

    current_product_id: str | None = Field(
        default=None,
        description="product_id of the product-detail page the shopper is on, if any.",
    )


class ProductCardOut(BaseModel):
    """A product as rendered on the site: catalogue/inventory row, no internal fields."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    image_url: str
    price: float
    inventory: list[dict]
    total_stock: int


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCardOut]
    model_used: str = Field(
        description="Which model actually answered this turn (Problem 9 smart-model toggle)."
    )


class ChatHistoryEntry(BaseModel):
    """One stored turn from chat_messages, replayed to rebuild the widget on return."""

    role: str
    content: str
    products: list[ProductCardOut] = Field(default_factory=list)
    created_at: str


class AuditEntry(BaseModel):
    """One row of the append-only agent audit trail (output/audit_trail.json).

    One entry per tool call the agent actually made during a run — not one
    entry per chat turn — so the trail shows the real reasoning path (which
    tools, in what order, with what result) behind every reply.
    """

    timestamp: datetime
    tool_name: str
    tool_args: dict = Field(default_factory=dict)
    short_result: str = Field(description="Truncated string form of the tool's return value.")
    stop_reason: str = Field(description='"completed" for a normal finish, "error" if the run raised.')
