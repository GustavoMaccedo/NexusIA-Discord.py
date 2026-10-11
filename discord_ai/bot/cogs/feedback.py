import discord
from discord import app_commands
from discord.ext import commands

from ..storage.database import session_factory
from ..storage.models import Feedback


class FeedbackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="feedback", description="Avaliar resposta (1-5) + correção opcional")
    async def feedback(self, it: discord.Interaction, nota: int, correcao: str = ""):
        if not 1 <= nota <= 5:
            await it.response.send_message("Nota deve ser 1-5.", ephemeral=True)
            return
        import hashlib

        gh = hashlib.sha256(f"guild:{it.guild_id}".encode()).hexdigest()[:16]
        try:
            async with session_factory() as s:
                s.add(Feedback(guild_hash=gh, rating=nota, correction=correcao[:2000]))
                await s.commit()
        except Exception as e:  # noqa — ex.: banco fora
            await it.response.send_message(f"DB indisponível: {e}"[:1900], ephemeral=True)
            return
        await it.response.send_message(
            "Feedback registrado como pendente. Obrigado!", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(FeedbackCog(bot))
