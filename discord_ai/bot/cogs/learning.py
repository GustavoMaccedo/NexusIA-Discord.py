import discord
from discord import app_commands
from discord.ext import commands

from ..core.config import settings
from ..services import training_service


class Learning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aprendizado", description="Estado do treinamento")
    async def aprendizado(self, it: discord.Interaction):
        import json
        from pathlib import Path

        try:
            from ..storage import repositories as repo

            stats = await repo.example_stats()
            fila = f"fila=total {stats['total']}/pending {stats['pending']}"
        except Exception as e:  # noqa — mostra o motivo em vez de "?"
            fila = f"fila=ERRO({type(e).__name__})"
        try:
            from ..services import checkpoint_service as ckpt

            info = ckpt.active_info()
            modelo = f"modelo={info.get('dataset_id', '?')}/val {info.get('metrics', {}).get('val_loss', '?')}"
        except Exception:  # noqa
            modelo = "modelo=?"
        lp = Path("logs/continual_last.json")
        if lp.exists():
            try:
                d = json.loads(lp.read_text())
                last = json.dumps(
                    {k: d.get(k) for k in ("status", "n_new", "val_loss", "decision", "promoted")},
                    ensure_ascii=False,
                )[:400]
            except Exception:  # noqa
                last = "ilegível"
        else:
            last = "nenhum ciclo ainda"
        await it.response.send_message(
            f"ingestion={settings.DISCORD_TRAINING_INGESTION_ENABLED} {fila} {modelo} ultimo_ciclo={last}",
            ephemeral=True,
        )

    @app_commands.command(name="treinar", description="Dispara treino em subprocesso (admin)")
    @app_commands.checks.has_permissions(administrator=True)
    async def treinar(self, it: discord.Interaction):
        try:
            pid = training_service.start_training_subprocess()
            await it.response.send_message(f"Treino disparado pid={pid}", ephemeral=True)
        except Exception as e:  # noqa
            await it.response.send_message(f"Falha: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Learning(bot))
