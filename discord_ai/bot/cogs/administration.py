import discord
from discord import app_commands
from discord.ext import commands

from ..services import checkpoint_service as ckpt
from ..storage import repositories as repo


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin", description="Administração")
    @app_commands.describe(acao="modelo|avaliacao|rollback|esquecer", arg="hash ou vazio")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin(self, it: discord.Interaction, acao: str, arg: str = ""):
        if acao == "modelo":
            await it.response.send_message(str(ckpt.active_info())[:1900], ephemeral=True)
        elif acao == "esquecer":
            try:
                n = await repo.delete_by_hash(arg.strip(), "pedido admin")
            except Exception as e:  # noqa — ex.: banco fora
                await it.response.send_message(f"DB indisponível: {e}"[:1900], ephemeral=True)
                return
            await it.response.send_message(
                f"Marcados como excluídos: {n}. Reconstrua checkpoint sem esses dados.",
                ephemeral=True,
            )
        else:
            await it.response.send_message(
                f"Ação {acao}: use scripts/evaluate_model.py e promotion.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Admin(bot))
