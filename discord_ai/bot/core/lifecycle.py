from __future__ import annotations

from .logging_config import get_logger

log = get_logger("nexusia.lifecycle")
COGS = [
    "discord_ai.bot.cogs.chat",
    "discord_ai.bot.cogs.watch",
    "discord_ai.bot.cogs.feedback",
    "discord_ai.bot.cogs.learning",
    "discord_ai.bot.cogs.memory",
    "discord_ai.bot.cogs.administration",
]


async def setup_hook(bot) -> None:
    for ext in COGS:
        try:
            await bot.load_extension(ext)
        except Exception as e:  # noqa
            log.warning("cog %s falhou: %s", ext, e)


async def on_ready_sync(bot) -> None:
    try:
        await bot.tree.sync()
        log.info("slash commands sincronizados")
    except Exception as e:  # noqa
        log.warning("sync falhou: %s", e)
