from __future__ import annotations

import asyncio

from .core.client import build_bot
from .core.config import settings
from .core.lifecycle import on_ready_sync, setup_hook
from .core.logging_config import get_logger, setup_logging

log = get_logger("nexusia.main")


async def amain() -> None:
    setup_logging(settings.LOG_LEVEL)
    if not settings.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN ausente no .env")
    if "+asyncpg" not in settings.DATABASE_URL and "+aiosqlite" not in settings.DATABASE_URL:
        raise SystemExit(
            f"DATABASE_URL sem driver async: {settings.DATABASE_URL.split('://')[0]}://..."
        )
    if not settings.chat_channels:
        log.warning("CHAT_CHANNEL_ID vazio: chat e watch desligados em silêncio")

    try:
        from .storage import init_models

        await init_models(settings.DATABASE_URL)
        log.info("banco pronto")
    except Exception as e:  # noqa — bot sobe p/ conversar; comandos de dados avisam
        log.error("banco indisponível no startup: %s", e)

    try:
        from .services.inference_service import _load

        await asyncio.to_thread(_load)
        log.info("modelo ativo pré-carregado")
    except Exception as e:  # noqa — bot sobe mesmo sem modelo; chat avisa no canal
        log.warning("modelo não pré-carregado: %s", e)
    bot = build_bot()

    @bot.event
    async def on_ready():
        log.info("logado como %s", bot.user)
        await on_ready_sync(bot)

    await setup_hook(bot)
    await bot.start(settings.DISCORD_TOKEN)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
