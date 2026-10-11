from __future__ import annotations

import re

BLOCK = [r"https?://\S+", r"<@!?\d+>", r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"]


def needs_review(text: str) -> str | None:
    for pat in BLOCK:
        if re.search(pat, text):
            return f"block:{pat}"
    return None
