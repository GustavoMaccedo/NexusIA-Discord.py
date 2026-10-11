from __future__ import annotations

_hist: dict[str, list[dict]] = {}


def push(session: str, role: str, text: str, limit: int = 10) -> None:
    _hist.setdefault(session, []).append({"role": role, "text": text})
    _hist[session] = _hist[session][-limit:]


def context_block(session: str) -> str:
    parts = []
    for m in _hist.get(session, [])[-6:]:
        who = "<usr>" if m["role"] == "user" else "<asst>"
        parts.append(f"{who}{m['text']}")
    return "<sep>".join(parts)


def should_auto_reply(
    channel_id: str | int | None,
    author_is_bot: bool,
    content: str,
    configured: set[str],
    command_prefix: str = "!",
    *,
    author_id: str | int | None = None,
    trainers: set[str] | frozenset = frozenset(),
) -> tuple[bool, str]:

    if author_is_bot and str(author_id) not in set(trainers):
        return False, "bot_author"
    if not configured:
        return False, "no_channel_configured"
    if str(channel_id) not in configured:
        return False, "other_channel"
    if not (content or "").strip():
        return False, "empty"
    if content.strip().startswith(command_prefix):
        return False, "command_prefix"
    return True, "ok"


def channel_session(channel_id: str | int, user_id: str | int) -> str:
    return f"chan:{channel_id}:user:{user_id}"
