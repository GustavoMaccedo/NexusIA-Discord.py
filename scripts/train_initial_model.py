#!/usr/bin/env python3


import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="datasets/incoming")
    ap.add_argument("--out", default="checkpoints/active")
    ap.add_argument("--vocab", type=int, default=8000)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--seq", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=256)
    ap.add_argument("--n-layer", type=int, default=6)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--dataset-id", default="seed-v1")
    ap.add_argument(
        "--resume", action="store_true", help="continua de out/model.pt próprio, se existir"
    )
    a = ap.parse_args()

    from discord_ai.model.tokenizer import NexusiaTokenizer
    from discord_ai.training.corpus_reader import corpus_from_dir

    texts = corpus_from_dir(a.corpus)
    assert texts, "corpus vazio — rode initialize_project.py"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tok_path = str(out / "tokenizer.json")
    try:
        tok = NexusiaTokenizer.train_from_texts(texts, vocab_size=a.vocab, save_path=tok_path)
        print(f"tokenizador BPE: vocab={tok.vocab_size}")
    except Exception as e:  # noqa: BLE001 — CLI: qualquer erro de treino do tok vira msg e sai
        print(f"BPE falhou ({e}), usando fallback não persistido p/ teste")
        return
    tokenized = [tok.encode(t) for t in texts]
    import random

    rng = random.Random(42)
    rng.shuffle(tokenized)
    n = len(tokenized)
    tr, va = tokenized[: int(n * 0.9)] or tokenized, tokenized[int(n * 0.9) :] or tokenized
    from discord_ai.model.config import ModelConfig

    cfg = ModelConfig(
        vocab_size=tok.vocab_size,
        d_model=a.d_model,
        n_layer=a.n_layer,
        n_head=a.n_head,
        d_ff=a.d_ff,
    )
    from discord_ai.training.train_model import train_model

    m = train_model(
        tr,
        va,
        cfg.to_dict(),
        out_dir=a.out,
        epochs=a.epochs,
        batch_size=a.batch,
        seq_len=a.seq,
        dataset_id=a.dataset_id,
        tokenizer_path=tok_path,
        lr=a.lr,
        resume_ckpt=str(out / "model.pt") if a.resume else None,
    )
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
