"""Shared Portkey-wired OpenAI client factory.

One place that knows how to reach OpenAI models through Portkey, used by both
the main chat agent (agent.py) and the semantic-search reranker
(semantic_search.py) so the connection setup isn't duplicated.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parent.parent / ".env")  # project root .env holds PORTKEY_API_KEY


def get_portkey_client() -> AsyncOpenAI:
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is missing from the project .env")
    return AsyncOpenAI(
        api_key=key,
        base_url="https://api.portkey.ai/v1",
        default_headers={"x-portkey-api-key": key, "x-portkey-provider": "openai"},
    )
