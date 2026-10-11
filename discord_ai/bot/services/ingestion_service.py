from __future__ import annotations

import hashlib

from ...training.preprocessing import is_eligible, text_hash
from ..storage import repositories as repo
from .moderation_service import needs_review
from .permission_service import require_ingestion


def pseudonymize(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


async def ingest_message(guild_id: str, text: str, scope: str = "guild") -> dict:
    require_ingestion(guild_id)
    ok, reason = is_eligible(text)
    if not ok:
        return {"stored": False, "reason": reason}
    if needs_review(text):
        return {"stored": False, "reason": "needs_review"}
    gh = pseudonymize(f"guild:{guild_id}")
    stored = await repo.add_example(gh, text.strip(), text_hash(text.strip()), scope)
    return {"stored": stored, "reason": "ok" if stored else "duplicate"}
