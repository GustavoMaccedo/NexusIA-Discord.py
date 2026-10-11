from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_engine = None
_Session = None


def init_db(database_url: str):
    global _engine, _Session
    connect_args = {}
    if "neon.tech" in database_url or "+asyncpg" in database_url:
        connect_args = {"statement_cache_size": 0}
    _engine = create_async_engine(
        database_url, echo=False, pool_pre_ping=True, connect_args=connect_args
    )
    _Session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


def session_factory():
    if _Session is None:
        raise RuntimeError("init_db() não chamado — chame init_models() no startup")
    return _Session()


def get_engine():
    return _engine
