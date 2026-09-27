"""Campus Customs chat agent: PydanticAI agent wired to OpenAI via Portkey.

Loads its system prompt from prompts/prompt.md and its tools from tools.py.
Grown in later problems (more tools, more safety rules) without changing the
FastAPI route that calls it.
"""
import os

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")  # keep server logs clean

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from audit import build_entries, log_error, append_audit
from models import ChatAgentReply, ProductInfo, PublicUser
from tools import check_size_stock, find_alternatives, get_product_info, get_stock, search_products

# Loop limits (Problem 12): bounds how many model round-trips / tool calls one
# chat turn can make, so a confused model can't loop indefinitely and run up
# cost. 10 requests / 8 tool calls is generous headroom over the 2-3 calls a
# normal turn needs (search -> info/stock -> maybe alternatives).
RUN_USAGE_LIMITS = UsageLimits(request_limit=10, tool_calls_limit=8)

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"

# Default per AI_prompts.md Problem 1: luna for normal turns, astra/terra for harder
# steps (flagged explicitly, not swapped in automatically).
DEFAULT_MODEL = "gpt-5.6-luna"
# Problem 9: on-demand smarter model, confirmed live against Portkey. Not exposed as
# a UI toggle — the shopper asks for it in plain language (see wants_smart_model),
# same pattern as flagging Astra/Terra to the user rather than auto-swapping models.
SMART_MODEL = "gpt-6-astra"

_SMART_MODEL_PATTERNS = [
    "gpt-6-astra", "gpt 6 astra", "smarter model", "better model", "stronger model",
    "more powerful model", "upgrade the model", "think harder", "use astra", "try astra",
]


def wants_smart_model(message: str) -> bool:
    """Detect a plain-language request to escalate to the smarter model.

    No visible "advanced settings" toggle in the UI — the assistant tells the
    shopper up front (see ChatWidget's greeting) that gpt-5.6-luna answers by
    default and that they can just ask for the smarter model if unhappy with a
    reply, and this is how that request gets picked up.
    """
    lowered = message.lower()
    return any(pattern in lowered for pattern in _SMART_MODEL_PATTERNS)


load_dotenv(HERE.parent.parent / ".env")  # project root .env holds PORTKEY_API_KEY


@dataclass
class ChatDeps:
    """Per-request context injected into the agent — the "who's chatting, what are
    they looking at" pattern. Never put in the prompt text directly; carried as
    typed deps so it's available to dynamic system-prompt functions and, if a
    future tool needs it, to tools too (via RunContext[ChatDeps]).
    """

    user: PublicUser | None = None
    current_product: ProductInfo | None = None
    escalated: bool = False


def make_chat_agent(model_name: str = DEFAULT_MODEL) -> Agent:
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is missing from the project .env")

    client = AsyncOpenAI(
        api_key=key,
        base_url="https://api.portkey.ai/v1",
        default_headers={"x-portkey-api-key": key, "x-portkey-provider": "openai"},
    )
    provider = OpenAIProvider(openai_client=client)
    # gpt-6-series reasoning models reject function tools on /v1/chat/completions
    # (confirmed live: 400 "Function tools with reasoning_effort are not supported
    # for gpt-6-astra... use /v1/responses"). The Responses API supports them, so
    # route those models through OpenAIResponsesModel instead of OpenAIChatModel.
    model = OpenAIResponsesModel(model_name, provider=provider) if model_name.startswith("gpt-6") else OpenAIChatModel(model_name, provider=provider)
    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=ChatAgentReply,
        retries=1,
        system_prompt=PROMPT_PATH.read_text(),
    )
    agent.tool_plain(search_products)
    agent.tool_plain(get_product_info)
    agent.tool_plain(get_stock)
    agent.tool_plain(check_size_stock)
    agent.tool_plain(find_alternatives)

    @agent.system_prompt
    def customer_and_page_context(ctx: RunContext[ChatDeps]) -> str:
        lines: list[str] = []
        if ctx.deps.user:
            u = ctx.deps.user
            lines.append(
                f"You are chatting with a logged-in shopper: {u.first_name} {u.last_name} "
                f"(email: {u.email}). You may address them by first name and pick up earlier "
                "context naturally, but never invent account details beyond this."
            )
        else:
            lines.append(
                "This shopper is browsing as a guest — no account is logged in. Don't address "
                "them by name or assume any account details."
            )
        if ctx.deps.current_product:
            p = ctx.deps.current_product
            lines.append(
                f'Page context: the shopper is currently viewing the product page for "{p.name}" '
                f"(product_id: {p.product_id}), priced ${p.price:.2f}, described as: {p.description} "
                f"Available colors: {', '.join(p.colors)}. If they ask something like \"do you have "
                'this in pink?" or "is this in stock?" without naming a product, resolve "this"/"it" '
                "to this product_id — call get_product_info/get_stock/check_size_stock on it directly "
                "rather than asking them to repeat the name, unless the conversation clearly points to "
                "a different product."
            )
        if ctx.deps.escalated:
            lines.append(
                "You are answering this turn as the smarter/upgraded model, because the shopper asked "
                "for extra reasoning power (or named it directly). You can switch models — briefly "
                "acknowledge that you're using it for this one, don't deny the capability."
            )
        return "\n\n".join(lines)

    return agent


# Agents are cached per model name (not rebuilt per request) — constructing a new
# AsyncOpenAI client/Agent on every chat turn would be wasteful; there are only
# ever two entries in this cache (default + smart) in practice.
_agent_cache: dict[str, Agent] = {}


def get_chat_agent(model_name: str = DEFAULT_MODEL) -> Agent:
    if model_name not in _agent_cache:
        _agent_cache[model_name] = make_chat_agent(model_name)
    return _agent_cache[model_name]


async def run_chat(
    message: str,
    deps: ChatDeps | None = None,
    model_name: str = DEFAULT_MODEL,
) -> ChatAgentReply:
    agent = get_chat_agent(model_name)
    try:
        result = await agent.run(message, deps=deps or ChatDeps(), usage_limits=RUN_USAGE_LIMITS)
    except Exception as exc:
        log_error(model_name, exc)
        raise
    append_audit(build_entries(result.new_messages(), stop_reason="completed"))
    return result.output
