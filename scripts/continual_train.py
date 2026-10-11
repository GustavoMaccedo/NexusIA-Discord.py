#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import glob
import json
import math
import os
import random
import shutil
import sys
import time
from pathlib import Path


def _parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Um ciclo de continual training via fila do Discord.")
    ap.add_argument("--min-new", type=int, default=50)
    ap.add_argument("--max-new", type=int, default=500)
    ap.add_argument("--rehearsal", type=int, default=200)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--steps-cap", type=int, default=300)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--seq", type=int, default=64)
    ap.add_argument("--active", default="checkpoints/active")
    ap.add_argument(
        "--out",
        default=None,
        help="Dir do candidato. Default: checkpoints/candidates/continual-<timestamp>.",
    )
    a = ap.parse_args(argv)
    if not a.out:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        a.out = f"checkpoints/candidates/continual-{stamp}"
    return a


def _load_env_database_url() -> str:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except Exception:  # noqa: BLE001, S110 — dotenv opcional; fallback é o default sqlite
        pass
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nexusia.db")


def _read_rehearsal_lines(limit: int) -> list[str]:
    if limit <= 0:
        return []
    lines: list[str] = []
    for path in sorted(glob.glob("datasets/incoming/*.txt")):
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    t = line.strip()
                    if t:
                        lines.append(t)
                    if len(lines) >= limit:
                        break
        except FileNotFoundError:
            continue
        if len(lines) >= limit:
            break
    return lines[:limit]


async def _amain(a: argparse.Namespace) -> dict:
    from discord_ai.bot.storage import init_models
    from discord_ai.bot.storage.repositories import mark_used, pending_examples
    from discord_ai.training.preprocessing import deduplicate, is_eligible, text_hash

    await init_models(_load_env_database_url())

    pending = await pending_examples(limit=a.max_new)
    if len(pending) < a.min_new:
        res = {"status": "idle", "pending": len(pending)}
        print(json.dumps(res, ensure_ascii=False))
        return res

    eligible_texts: list[str] = []
    eligible_hashes: list[str] = []
    for _guild_hash, content, content_hash in pending:
        ok, _reason = is_eligible(content)
        if ok:
            eligible_texts.append(content)
            eligible_hashes.append(content_hash)

    seen: set[str] = set()
    new_texts: list[str] = []
    new_hashes: list[str] = []
    for t, h in zip(eligible_texts, eligible_hashes):
        _ = deduplicate
        hh = text_hash(t)
        if hh not in seen:
            seen.add(hh)
            new_texts.append(t)
            new_hashes.append(h)
    if len(new_texts) < a.min_new:
        res = {
            "status": "idle",
            "pending": len(new_texts),
            "reason": f"apos filtro/dedup: {len(new_texts)} < min-new {a.min_new}",
        }
        print(json.dumps(res, ensure_ascii=False))
        return res

    rehearsal_texts = _read_rehearsal_lines(a.rehearsal)

    pool: list[tuple[str, str | None]] = [(t, h) for t, h in zip(new_texts, new_hashes)]
    pool += [(t, None) for t in rehearsal_texts]
    rng = random.Random(123)
    rng.shuffle(pool)

    from discord_ai.model.tokenizer import NexusiaTokenizer

    tok_path = str(Path(a.active) / "tokenizer.json")
    meta_path = Path(a.active) / "meta.json"
    tokenizer = NexusiaTokenizer.load(tok_path)
    if not meta_path.exists():
        res = {"status": "error", "reason": f"active sem meta.json em {meta_path}"}
        print(json.dumps(res, ensure_ascii=False))
        return res
    active_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    config_dict = active_meta.get("config") or {}
    if not config_dict:
        res = {"status": "error", "reason": f"active meta.json sem 'config': {meta_path}"}
        print(json.dumps(res, ensure_ascii=False))
        return res
    active_metrics = active_meta.get("metrics")
    if tokenizer.vocab_size != config_dict.get("vocab_size"):
        res = {
            "status": "error",
            "reason": f"tokenizer vocab {tokenizer.vocab_size} != config {config_dict.get('vocab_size')} (par trocado? restaure o backup)",
        }
        print(json.dumps(res, ensure_ascii=False))
        return res

    tokenized_pool: list[list[int]] = [tokenizer.encode(t) for t, _ in pool]
    pool_hashes: list[str | None] = [h for _, h in pool]

    idx = list(range(len(tokenized_pool)))
    random.Random(123).shuffle(idx)
    n_train = int(len(idx) * 0.9)
    train_idx = idx[:n_train] or idx
    test_idx = idx[n_train:] or idx[-1:]
    tokenized_train = [tokenized_pool[i] for i in train_idx]
    tokenized_test = [tokenized_pool[i] for i in test_idx]

    est_steps = math.ceil(len(tokenized_train) / max(1, a.batch))
    truncated = False
    if est_steps > a.steps_cap:
        keep = max(1, a.steps_cap * a.batch)
        kept_idx = train_idx[:keep]
        tokenized_train = [tokenized_pool[i] for i in kept_idx]
        truncated = True
        used_idx_set = set(kept_idx) | set(test_idx)
    else:
        used_idx_set = set(train_idx) | set(test_idx)
    evaluated_hashes = sorted({pool_hashes[i] for i in used_idx_set if pool_hashes[i]})

    from discord_ai.training.train_model import evaluate_model_dir, train_model

    active_ckpt = str(Path(a.active) / "model.pt")
    train_metrics = train_model(
        tokenized_train,
        tokenized_test,
        config_dict,
        out_dir=a.out,
        epochs=1,
        batch_size=a.batch,
        lr=a.lr,
        seq_len=a.seq,
        dataset_id=f"continual-{time.strftime('%Y%m%d-%H%M%S')}",
        tokenizer_path=tok_path,
        resume_ckpt=active_ckpt if Path(active_ckpt).exists() else None,
    )

    try:
        dst_tok = Path(a.out) / "tokenizer.json"
        if not dst_tok.exists() and Path(tok_path).exists():
            dst_tok.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tok_path, dst_tok)
    except Exception:  # noqa: BLE001, S110 — cópia best-effort; treino não depende dela
        pass

    eval_metrics = evaluate_model_dir(a.out, tokenized_test, seq_len=a.seq)
    cand_for_decision = {"val_loss": eval_metrics.get("test_loss", 9e9)}

    from discord_ai.training.promotion import promote_candidate, promotion_decision

    approved, decision = promotion_decision(cand_for_decision, active_metrics)
    if approved:
        promote_candidate(a.out, a.active)

    if evaluated_hashes:
        await mark_used(evaluated_hashes)

    res = {
        "status": "promoted" if approved else "rejected",
        "n_new": len(new_texts),
        "n_rehearsal": len(rehearsal_texts),
        "val_loss": cand_for_decision["val_loss"],
        "train_val_loss": train_metrics.get("val_loss"),
        "active_val_loss": (active_metrics or {}).get("val_loss") if active_metrics else None,
        "decision": decision,
        "promoted": bool(approved),
        "out": a.out,
        "train_samples": len(tokenized_train),
        "test_samples": len(tokenized_test),
        "train_truncated": truncated,
        "steps_cap": a.steps_cap,
        "est_steps_full": est_steps,
        "marked_used": len(evaluated_hashes),
    }
    print(json.dumps(res, ensure_ascii=False))
    return res


def main(argv=None) -> dict:
    a = _parse_args(argv)
    try:
        return asyncio.run(_amain(a))
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — guarda geral: erro vira JSON, nunca corrompe active
        import traceback

        res = {
            "status": "error",
            "reason": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(limit=8),
        }
        print(json.dumps(res, ensure_ascii=False))
        return res


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get("status") != "error" else 1)
