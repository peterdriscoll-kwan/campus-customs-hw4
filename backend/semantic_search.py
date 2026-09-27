"""LLM-based semantic reranking for product search.

Why an LLM rerank instead of embeddings: this Portkey account's config only
exposes chat-completion deployments (confirmed live — every embedding model
name tried came back "The embeddings operation does not work with the
specified model, gpt-5.6-luna", i.e. /v1/embeddings has no working deployment
here). A small dedicated agent judges relevance by meaning instead, which
actually understands intent ("something cozy for game day") rather than just
comparing vectors — arguably a better fit for a catalogue this small (~100
items) than building a vector index would have been.
"""
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from portkey_client import get_portkey_client

_MODEL = "gpt-5.6-luna"

_SYSTEM_PROMPT = (
    "You are a product-search relevance judge for a Yale campus merchandise shop. "
    "You'll be given a shopper's query and a compact catalogue list (product_id, name, "
    "garment type, colors, tags). Return the product_ids that are genuinely relevant to "
    "the query's meaning and intent, not just literal keyword overlap — e.g. \"something "
    "cozy for game day\" should surface hoodies/fleece jackets even though those words "
    "don't appear in the query. Rank most-relevant first. Only return ids that actually "
    "appear in the supplied catalogue list; never invent one. Return an empty list if "
    "nothing in the catalogue is a good match."
)


class SemanticMatches(BaseModel):
    product_ids: list[str] = Field(default_factory=list)


_agent: Agent | None = None


def _get_agent() -> Agent:
    global _agent
    if _agent is None:
        provider = OpenAIProvider(openai_client=get_portkey_client())
        _agent = Agent(
            OpenAIChatModel(_MODEL, provider=provider),
            output_type=SemanticMatches,
            retries=1,
            system_prompt=_SYSTEM_PROMPT,
        )
    return _agent


async def semantic_rerank(query: str, candidates: list[dict], limit: int) -> list[str]:
    """Return up to `limit` product_ids from `candidates` relevant to `query`, by meaning.

    `candidates` items need product_id/name/garment_type/colors/search_tags keys.
    Returns [] (never raises) on any failure — callers should treat this as "no
    semantic matches" and fall back to keyword search, not as an error.
    """
    if not candidates:
        return []
    valid_ids = {c["product_id"] for c in candidates}
    catalogue_lines = "\n".join(
        f"- {c['product_id']}: {c['name']} ({c['garment_type']}), "
        f"colors={c['colors']}, tags={c['search_tags'][:6]}"
        for c in candidates
    )
    prompt = f'Shopper query: "{query}"\n\nCatalogue:\n{catalogue_lines}\n\nReturn up to {limit} relevant product_ids.'
    try:
        result = await _get_agent().run(prompt)
    except Exception:
        return []
    # Defensive: only trust ids that actually exist in the catalogue we sent,
    # same "never trust an LLM id blindly" pattern as the rest of the app.
    return [pid for pid in result.output.product_ids if pid in valid_ids][:limit]
