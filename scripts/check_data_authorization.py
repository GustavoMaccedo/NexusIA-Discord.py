#!/usr/bin/env python3


import os

from dotenv import load_dotenv

load_dotenv()
v = os.getenv("DISCORD_TRAINING_INGESTION_ENABLED", "false").lower() == "true"
print(f"DISCORD_TRAINING_INGESTION_ENABLED={v}")
if v:
    print("AVISO: ingestão ativa — confirme base legal, allowlist e política de exclusão.")
else:
    print("OK: ingestão desabilitada — nenhum dado coletado p/ treino.")
