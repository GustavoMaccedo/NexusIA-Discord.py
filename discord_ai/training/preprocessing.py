from __future__ import annotations

import hashlib
import re

ADMIN_PREFIXES = ("/admin", "!admin", "/ia aprendizado", "/ia dataset")


def text_hash(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()[:16]


def is_eligible(text: str, min_chars: int = 8, max_chars: int = 2000) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "empty"
    if len(text.strip()) < min_chars:
        return False, "too_short"
    if len(text) > max_chars:
        return False, "too_long"
    if text.startswith(ADMIN_PREFIXES):
        return False, "admin_command"
    if len(set(text.split())) <= 2 and len(text.split()) > 6:
        return False, "spam_repetition"
    if re.match(r"^(.)\1{10,}$", text.strip()):
        return False, "spam"
    return True, "ok"


def serialize_dialog(user: str, assistant: str | None = None) -> str:
    return f"<bos><usr>{user.strip()}<sep><asst>" + (
        f"{assistant.strip()}<eos>" if assistant else ""
    )


def deduplicate(texts: list[str]) -> list[str]:
    seen, out = set(), []
    for t in texts:
        h = text_hash(t)
        if h not in seen:
            seen.add(h)
            out.append(t)
    return out


def split_train_val_test(items: list, train: float = 0.85, val: float = 0.10, seed: int = 42):
    import random

    rng = random.Random(seed)
    idx = list(range(len(items)))
    rng.shuffle(idx)
    n_tr = int(len(items) * train)
    n_v = int(len(items) * val)
    tr = [items[i] for i in idx[:n_tr]]
    va = [items[i] for i in idx[n_tr : n_tr + n_v]]
    te = [items[i] for i in idx[n_tr + n_v :]]

    assert not (set(map(text_hash, tr)) & set(map(text_hash, te)))
    return tr, va, te
