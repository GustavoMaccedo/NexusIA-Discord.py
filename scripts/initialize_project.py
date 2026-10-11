#!/usr/bin/env python3


import asyncio
import shutil
from pathlib import Path

for d in [
    "checkpoints/active",
    "checkpoints/candidates",
    "datasets/incoming",
    "datasets/prepared",
    "datasets/evaluation",
    "logs",
]:
    Path(d).mkdir(parents=True, exist_ok=True)
if not Path(".env").exists() and Path(".env.example").exists():
    shutil.copy(".env.example", ".env")
    print("criado .env a partir do exemplo (preencha DISCORD_TOKEN/DATABASE_URL)")
seed = Path("datasets/incoming/seed_dialogues_ptbr.txt")
if not seed.exists():
    seed.write_text(
        "<bos><usr>Olá!<sep><asst>Olá! Como posso ajudar?<eos>\n"
        "<bos><usr>Bom dia!<sep><asst>Bom dia! Em que posso ser útil?<eos>\n"
        "<bos><usr>O que você é?<sep><asst>Sou a Nexusia, uma IA em treinamento.<eos>\n"
        "<bos><usr>Obrigado<sep><asst>Por nada! Precisando, é só chamar.<eos>\n",
        encoding="utf-8",
    )
    print("seed corpus criado")


async def _db():
    import os

    from dotenv import load_dotenv

    load_dotenv()
    from discord_ai.bot.storage import init_models

    await init_models(os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nexusia.db"))
    print("DB pronto")


asyncio.run(_db())
print("init ok")
