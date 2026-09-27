"""Append-only audit trail of agent tool-call activity (Problem 12).

Every real run_chat() call appends its tool-call trace here — never wipes
prior entries. Reads the existing JSON array (if any), appends, writes the
whole array back under a lock, same pattern as Homework 3's audit_trail.json.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart

from models import AuditEntry

HERE = Path(__file__).resolve().parent
AUDIT_PATH = HERE.parent / "output" / "audit_trail.json"
_LOCK = Lock()

# pydantic-ai's own synthetic tool call for delivering structured output --
# not one of our real tools, so it's excluded from the trail.
_INTERNAL_TOOL_NAMES = {"final_result"}


def _short(value, limit: int = 240) -> str:
    if isinstance(value, list):
        text = "[" + ", ".join(_short(item, limit=80) for item in value) + "]"
    elif hasattr(value, "model_dump_json"):
        text = value.model_dump_json()
    else:
        text = str(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def build_entries(messages: list[ModelMessage], stop_reason: str) -> list[AuditEntry]:
    """Walk a run's messages and pair each real tool call with its return value."""
    pending: dict[str, ToolCallPart] = {}
    entries: list[AuditEntry] = []
    for message in messages:
        for part in getattr(message, "parts", []):
            if isinstance(part, ToolCallPart) and part.tool_name not in _INTERNAL_TOOL_NAMES:
                pending[part.tool_call_id] = part
            elif isinstance(part, ToolReturnPart):
                call = pending.pop(part.tool_call_id, None)
                if call is None:
                    continue
                try:
                    args = json.loads(call.args) if isinstance(call.args, str) else dict(call.args or {})
                except (json.JSONDecodeError, TypeError):
                    args = {"_raw": str(call.args)}
                entries.append(
                    AuditEntry(
                        timestamp=part.timestamp or datetime.now(timezone.utc),
                        tool_name=call.tool_name,
                        tool_args=args,
                        short_result=_short(part.content),
                        stop_reason=stop_reason,
                    )
                )
    return entries


def append_audit(entries: list[AuditEntry]) -> None:
    if not entries:
        return
    with _LOCK:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            existing = json.loads(AUDIT_PATH.read_text()) if AUDIT_PATH.exists() else []
            if not isinstance(existing, list):
                existing = []
        except (OSError, ValueError):
            existing = []
        existing.extend(e.model_dump(mode="json") for e in entries)
        AUDIT_PATH.write_text(json.dumps(existing, indent=2) + "\n")


def log_error(model_name: str, error: Exception) -> None:
    append_audit(
        [
            AuditEntry(
                timestamp=datetime.now(timezone.utc),
                tool_name="(agent_run)",
                tool_args={"model": model_name},
                short_result=_short(f"{type(error).__name__}: {error}"),
                stop_reason="error",
            )
        ]
    )
