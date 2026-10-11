#!/usr/bin/env python3


import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="checkpoints/active")
    ap.add_argument("--prompt", default="Olá!")
    ap.add_argument("--max-new", type=int, default=64)
    a = ap.parse_args()
    from discord_ai.model.checkpoint import load_checkpoint
    from discord_ai.model.config import ModelConfig
    from discord_ai.model.generation import generate
    from discord_ai.model.language_model import GPTModel
    from discord_ai.model.tokenizer import NexusiaTokenizer

    meta = json.loads(Path(f"{a.ckpt}/meta.json").read_text())
    model = GPTModel(ModelConfig.from_dict(meta["config"]))
    load_checkpoint(model, f"{a.ckpt}/model.pt")
    tok = NexusiaTokenizer.load(f"{a.ckpt}/tokenizer.json")
    ids = tok.encode(f"<bos><usr>{a.prompt}<sep><asst>")
    out = generate(model, ids, max_new_tokens=a.max_new)
    print(tok.decode(out))


if __name__ == "__main__":
    main()
