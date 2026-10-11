from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from ..core.config import settings
from ..core.logging_config import get_logger
from ..services import checkpoint_service as ckpt
from ..services import conversation_service as conv
from ..services import inference_service
from ..utils.text import chunk

log = get_logger("nexusia.chat")

EMPTY_FALLBACK = (
    "Gerei uma resposta vazia — o modelo ainda está no início do treinamento. "
    "Tente reformular a frase."
)


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ia", description="Interage com a IA própria")
    @app_commands.describe(acao="conversar|status|modelo", texto="mensagem")
    async def ia(self, it: discord.Interaction, acao: str, texto: str = ""):
        if acao == "status":
            info = ckpt.active_info()
            await it.response.send_message(f"Modelo carregado: {info.get('loaded', False)}"[:1900])
            return
        if acao == "modelo":
            info = ckpt.active_info()
            await it.response.send_message(
                str({k: info.get(k) for k in ("origin", "dataset_id", "metrics")})[:1900]
            )
            return

        await it.response.defer()
        conv.push(str(it.user.id), "user", texto)
        try:
            r = await inference_service.generate_reply(
                conv.context_block(str(it.user.id)) + f"<sep><usr>{texto}<sep><asst>"
            )
        except Exception as e:  # noqa
            await it.followup.send(f"Modelo indisponível: {e}"[:1900])
            return
        if r.get("empty"):
            await it.followup.send(EMPTY_FALLBACK)
            return
        conv.push(str(it.user.id), "assistant", r["text"])
        await it.followup.send(chunk(r["text"])[0])

    @commands.Cog.listener("on_message")
    async def chat_no_canal(self, message: discord.Message) -> None:

        ok, _ = conv.should_auto_reply(
            getattr(message.channel, "id", None),
            getattr(message.author, "bot", False),
            getattr(message, "content", ""),
            settings.chat_channels,
            self.bot.command_prefix if isinstance(self.bot.command_prefix, str) else "!",
            author_id=getattr(message.author, "id", None),
            trainers=settings.trainer_bots,
        )
        if not ok:
            return
        sess = conv.channel_session(message.channel.id, message.author.id)
        texto = message.content.strip()[: settings.MAX_INPUT_TOKENS]
        conv.push(sess, "user", texto)
        try:
            async with message.channel.typing():
                r = await inference_service.generate_reply(
                    conv.context_block(sess) + f"<sep><usr>{texto}<sep><asst>"
                )
        except Exception as e:  # noqa — nunca derruba o event loop
            log.warning("inferência no canal falhou: %s", e)
            await message.reply("Modelo indisponível agora, tente de novo.", mention_author=False)
            return
        if not r.get("empty"):
            conv.push(sess, "assistant", r["text"])
        await message.reply(
            chunk(r["text"])[0] if not r.get("empty") else EMPTY_FALLBACK, mention_author=False
        )

        try:
            from ..services import ingestion_service

            await ingestion_service.ingest_message(str(message.guild.id), texto)
        except Exception:  # noqa — bloqueado/desabilitado por padrão
            pass


async def setup(bot):
    await bot.add_cog(Chat(bot))
