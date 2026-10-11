from __future__ import annotations

from .preprocessing import is_eligible

MIN_SIDE_CHARS = 8
MAX_SIDE_CHARS = 600
MAX_TOTAL_CHARS = 1500


def build_pair(parent_text: str | None, child_text: str | None) -> str | None:

    if not isinstance(parent_text, str) or not isinstance(child_text, str):
        return None
    parent, child = parent_text.strip(), child_text.strip()
    for side in (parent, child):
        ok, _ = is_eligible(side, min_chars=MIN_SIDE_CHARS, max_chars=MAX_SIDE_CHARS)
        if not ok:
            return None
    if len(parent) + len(child) > MAX_TOTAL_CHARS:
        return None
    line = f"<bos><usr>{parent}<sep><asst>{child}<eos>"
    if len(line) > MAX_TOTAL_CHARS + 64:
        return None
    return line


def build_single(text: str | None) -> str | None:

    if not isinstance(text, str):
        return None
    clean = text.strip()
    ok, _ = is_eligible(clean, min_chars=MIN_SIDE_CHARS, max_chars=MAX_SIDE_CHARS)
    if not ok:
        return None
    return f"<bos><usr>{clean}<eos>"
