import discord
from discord import app_commands
from discord.ext import commands

from ..core.config import settings
from ..storage import repositories as repo


class Memory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="privacidade", description="Controles de coleta")
    async def privacidade(self, it: discord.Interaction):
        await it.response.send_message(
            f"Coleta p/ treino: {'ATIVA' if settings.DISCORD_TRAINING_INGESTION_ENABLED else 'DESABILITADA'}. "
            "IDs pseudonimizados. Exclusão: peça a um admin /admin esquecer <hash>.",
            ephemeral=True,
        )

    @app_commands.command(name="dataset", description="Estatísticas sem conteúdo privado")
    async def dataset(self, it: discord.Interaction):
        try:
            s = await repo.example_stats()
            await it.response.send_message(f"Exemplos: {s}", ephemeral=True)
        except Exception as e:  # noqa
            await it.response.send_message(f"DB indisponível: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Memory(bot))
