#!/usr/bin/env python3


import argparse
import json

from discord_ai.model.tokenizer import NexusiaTokenizer
from discord_ai.training.corpus_reader import corpus_from_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="checkpoints/active")
    ap.add_argument("--corpus", default="datasets/incoming")
    a = ap.parse_args()
    tok = NexusiaTokenizer.load(f"{a.ckpt}/tokenizer.json")
    texts = corpus_from_dir(a.corpus)
    tokenized = [tok.encode(t) for t in texts]
    te = tokenized[int(len(tokenized) * 0.9) :] or tokenized
    from discord_ai.training.train_model import evaluate_model_dir

    print(json.dumps(evaluate_model_dir(a.ckpt, te), indent=2))


if __name__ == "__main__":
    main()
