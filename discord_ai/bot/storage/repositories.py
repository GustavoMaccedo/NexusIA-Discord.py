from __future__ import annotations

from sqlalchemy import func, select

from .database import session_factory
from .models import DeletionRecord, EligibleExample


async def add_example(
    guild_hash: str, content: str, content_hash: str, scope: str = "guild"
) -> bool:
    async with session_factory() as s:
        exists = (
            await s.execute(
                select(EligibleExample.id).where(
                    EligibleExample.guild_hash == guild_hash,
                    EligibleExample.content_hash == content_hash,
                )
            )
        ).first()
        if exists:
            return False
        s.add(
            EligibleExample(
                guild_hash=guild_hash, content=content, content_hash=content_hash, scope=scope
            )
        )
        await s.commit()
        return True


async def pending_examples(limit: int = 200):
    async with session_factory() as s:
        rows = (
            (
                await s.execute(
                    select(EligibleExample).where(EligibleExample.status == "pending").limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return [(r.guild_hash, r.content, r.content_hash) for r in rows]


async def mark_used(hashes: list[str]) -> None:
    async with session_factory() as s:
        rows = (
            (
                await s.execute(
                    select(EligibleExample).where(EligibleExample.content_hash.in_(hashes))
                )
            )
            .scalars()
            .all()
        )
        for r in rows:
            r.status = "used"
        await s.commit()


async def delete_by_hash(content_hash: str, reason: str = "") -> int:
    async with session_factory() as s:
        rows = (
            (
                await s.execute(
                    select(EligibleExample).where(EligibleExample.content_hash == content_hash)
                )
            )
            .scalars()
            .all()
        )
        n = len(rows)
        for r in rows:
            r.status = "deleted"
            r.content = "[deleted]"
        s.add(DeletionRecord(content_hash=content_hash, reason=reason))
        await s.commit()
        return n


async def example_stats():
    async with session_factory() as s:
        total = (await s.execute(select(func.count(EligibleExample.id)))).scalar() or 0
        pend = (
            await s.execute(
                select(func.count(EligibleExample.id)).where(EligibleExample.status == "pending")
            )
        ).scalar() or 0
        return {"total": total, "pending": pend}
