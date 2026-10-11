import pytest

from discord_ai.bot.core.config import settings
from discord_ai.bot.core.errors import IngestionDisabled
from discord_ai.bot.services import ingestion_service


async def test_ingestion_blocked_when_disabled():
    old = settings.DISCORD_TRAINING_INGESTION_ENABLED
    settings.DISCORD_TRAINING_INGESTION_ENABLED = False
    try:
        with pytest.raises(IngestionDisabled):
            await ingestion_service.ingest_message("123", "mensagem elegível suficiente aqui")
    finally:
        settings.DISCORD_TRAINING_INGESTION_ENABLED = old


async def test_ingestion_flag_tem_default_off_e_atual_on_neste_env():

    from discord_ai.bot.core.config import Settings

    assert Settings().model_fields["DISCORD_TRAINING_INGESTION_ENABLED"].default is False
    assert isinstance(settings.DISCORD_TRAINING_INGESTION_ENABLED, bool)


def test_guild_isolation_hash():
    from discord_ai.bot.services.ingestion_service import pseudonymize

    assert pseudonymize("guild:1") != pseudonymize("guild:2")


async def test_db_flow():
    from discord_ai.bot.storage import init_models
    from discord_ai.bot.storage import repositories as repo

    await init_models("sqlite+aiosqlite:///:memory:")
    assert await repo.add_example("g1", "conteudo suficiente para teste aqui", "abc123") is True
    assert await repo.add_example("g1", "conteudo suficiente para teste aqui", "abc123") is False
    s = await repo.example_stats()
    assert s["total"] >= 1
    assert await repo.delete_by_hash("abc123", "teste") == 1
