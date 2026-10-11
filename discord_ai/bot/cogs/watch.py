from __future__ import annotations

from discord.ext import commands

from ...training.pair_builder import build_pair, build_single
from ...training.preprocessing import text_hash
from ..core.config import settings
from ..services import ingestion_service
from ..services.moderation_service import needs_review
from ..storage import repositories


class Watch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_watch(self, message) -> None:

        try:
            if getattr(message.author, "bot", False):
                return
            channel_id = getattr(message.channel, "id", None)
            if str(channel_id) not in settings.chat_channels:
                return
            content = getattr(message, "content", "") or ""
            if not content.strip():
                return
            guild = getattr(message, "guild", None)
            guild_id = str(guild.id) if guild is not None else f"dm:{channel_id}"
            ref = getattr(message, "reference", None)
            parent_id = getattr(ref, "message_id", None) if ref is not None else None
            if parent_id:
                try:
                    parent = await message.channel.fetch_message(parent_id)
                except Exception:  # noqa: BLE001 — NotFound/HTTPException/Forbidden → single
                    parent = None
                if parent is not None and not getattr(parent.author, "bot", False):
                    pcontent = getattr(parent, "content", "") or ""
                    if pcontent.strip():
                        try:
                            pair = build_pair(pcontent, content)
                        except Exception:  # noqa: BLE001 — par inválido cai p/ single
                            pair = None
                        if pair is not None:
                            try:
                                if needs_review(pcontent) or needs_review(content):
                                    return
                                gh = ingestion_service.pseudonymize(f"guild:{guild_id}")
                                await repositories.add_example(
                                    gh, pair, text_hash(pair), "reply-pair"
                                )
                                return
                            except Exception:  # noqa: BLE001,S110 — cai p/ single
                                pass
            try:
                if needs_review(content):
                    return
                line = build_single(content)
                if line is None:
                    return
                gh = ingestion_service.pseudonymize(f"guild:{guild_id}")
                await repositories.add_example(gh, line, text_hash(line), "watch")
            except Exception:  # noqa: BLE001,S110 — IngestionDisabled etc. → silêncio
                pass
        except Exception:  # noqa: BLE001,S110 — best-effort total
            pass


async def setup(bot):
    await bot.add_cog(Watch(bot))
