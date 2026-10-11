from __future__ import annotations

from .database import get_engine, init_db
from .models import Base


async def init_models(database_url: str) -> None:
    init_db(database_url)
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
