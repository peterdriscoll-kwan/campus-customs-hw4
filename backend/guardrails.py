"""Safety/accuracy guardrail for chat replies (Problem 9).

The agent is already instructed to ground every price in a tool call (Problem 6),
and in practice it does. This is the safety net for the rare case it doesn't:
after a reply comes back, cross-check every dollar amount it mentions against the
real prices of the products resolved for that turn. A mismatch means the model
said a number nothing in the database backs up — a potential hallucination, and
exactly the kind of thing that must never reach a customer as fact.
"""
import re

from models import ProductCardOut

_PRICE_RE = re.compile(r"\$(\d+(?:\.\d{1,2})?)")


def find_price_mismatches(reply_text: str, products: list[ProductCardOut]) -> list[float]:
    """Dollar amounts in `reply_text` that don't match any resolved product's real
    price. Empty means every price mentioned is grounded in this turn's db data.
    """
    known_prices = {round(p.price, 2) for p in products}
    mentioned_prices = {round(float(m), 2) for m in _PRICE_RE.findall(reply_text)}
    return sorted(mentioned_prices - known_prices)


CORRECTION_NUDGE = (
    "SYSTEM CORRECTION — your previous answer to this exact question stated a price "
    "({mismatches}) that does not match any price a tool returned. Answer again from "
    "scratch: call the appropriate tool(s) again and state prices exactly as they "
    "come back, with no rounding or estimating."
)


def build_retry_message(original_message: str, mismatches: list[float]) -> str:
    mismatch_text = ", ".join(f"${m:.2f}" for m in mismatches)
    return f"{original_message}\n\n{CORRECTION_NUDGE.format(mismatches=mismatch_text)}"
