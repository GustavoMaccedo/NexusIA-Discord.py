from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ..model.checkpoint import load_checkpoint, save_checkpoint
from ..model.language_model import GPTModel
from .dataset import ConversationDataset
from .optimizer import build_optimizer, build_scheduler


def train_model(
    tokenized_train: list[list[int]],
    tokenized_val: list[list[int]],
    config_dict: dict,
    out_dir: str,
    epochs: int = 2,
    batch_size: int = 8,
    lr: float = 3e-4,
    seq_len: int = 128,
    grad_accum: int = 2,
    max_ram_mb: int = 1500,
    resume_ckpt: str | None = None,
    dataset_id: str = "seed-v1",
    tokenizer_path: str | None = None,
) -> dict:
    import psutil

    from ..model.config import ModelConfig

    cfg = ModelConfig.from_dict(config_dict)
    model = GPTModel(cfg)
    opt = build_optimizer(model, lr=lr)
    start_step = 0
    if resume_ckpt and Path(resume_ckpt).exists():
        load_checkpoint(model, resume_ckpt, None)

    train_ds = ConversationDataset(tokenized_train, seq_len)
    val_ds = ConversationDataset(tokenized_val, seq_len)
    dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    sched = build_scheduler(opt, total_steps=max(1, epochs * max(1, len(dl)) // grad_accum))

    hist = {"train_loss": [], "val_loss": [], "steps": 0}
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    tok_count = 0
    model.train()
    step = start_step
    prog_path = Path(out_dir) / "progress.jsonl"
    for ep in range(epochs):
        for xb, yb in dl:
            logits = model(xb)
            loss = (
                torch.nn.functional.cross_entropy(
                    logits.reshape(-1, logits.size(-1)), yb.reshape(-1)
                )
                / grad_accum
            )
            loss.backward()
            tok_count += xb.numel()
            if (step + 1) % grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                sched.step()
                opt.zero_grad()
                mem = psutil.Process().memory_info().rss / 1e6
                if mem > max_ram_mb:
                    raise MemoryError(f"RAM {mem:.0f}MB > limite {max_ram_mb}MB")
            step += 1
            if step % 25 == 0:
                dt = time.time() - t0
                rec = {
                    "step": step,
                    "epoch": ep,
                    "loss": round(float(loss.item() * grad_accum), 4),
                    "tok_s": round(tok_count / max(1e-6, dt), 1),
                    "rss_mb": round(
                        mem
                        if (step + 1) % grad_accum == 0
                        else psutil.Process().memory_info().rss / 1e6
                    ),
                    "elapsed_s": round(dt),
                }
                with open(prog_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(f"[ep{ep} step{step}] loss={rec['loss']} tok/s={rec['tok_s']}", flush=True)
            if step % 250 == 0:
                snap = Path(out_dir) / "snapshots" / f"step_{step}"
                save_checkpoint(
                    model,
                    opt,
                    sched,
                    config_dict,
                    tokenizer_path,
                    dataset_id,
                    {"step": step, "loss": round(float(loss.item() * grad_accum), 4)},
                    str(snap),
                )

        model.eval()
        with torch.no_grad():
            vl = 0.0
            n = 0
            for xb, yb in DataLoader(val_ds, batch_size=batch_size):
                vl += torch.nn.functional.cross_entropy(
                    model(xb).reshape(-1, model.config.vocab_size), yb.reshape(-1)
                ).item()
                n += 1
                if n >= 10:
                    break
            vl = vl / max(1, n)
        model.train()
        hist["train_loss"].append(float(loss.item() * grad_accum))
        hist["val_loss"].append(float(vl))
    hist["steps"] = step
    dt = time.time() - t0
    metrics = {
        "train_loss": hist["train_loss"][-1] if hist["train_loss"] else 0,
        "val_loss": hist["val_loss"][-1] if hist["val_loss"] else 0,
        "perplexity": math.exp(min(10, hist["val_loss"][-1])) if hist["val_loss"] else 0,
        "steps": step,
        "seconds": dt,
        "tokens": tok_count,
        "tok_per_s": tok_count / max(1e-6, dt),
    }
    save_checkpoint(model, opt, sched, config_dict, tokenizer_path, dataset_id, metrics, out_dir)
    (Path(out_dir) / "history.json").write_text(json.dumps(hist, indent=2))
    return metrics


def evaluate_model_dir(ckpt_dir: str, tokenized_test: list[list[int]], seq_len: int = 128) -> dict:
    import torch
    from torch.utils.data import DataLoader

    from ..model.config import ModelConfig

    meta = json.loads((Path(ckpt_dir) / "meta.json").read_text())
    model = GPTModel(ModelConfig.from_dict(meta["config"]))
    load_checkpoint(model, str(Path(ckpt_dir) / "model.pt"))
    model.eval()
    ds = ConversationDataset(tokenized_test, seq_len)
    tot, n = 0.0, 0
    with torch.no_grad():
        for xb, yb in DataLoader(ds, batch_size=8):
            tot += torch.nn.functional.cross_entropy(
                model(xb).reshape(-1, model.config.vocab_size), yb.reshape(-1)
            ).item()
            n += 1
    loss = tot / max(1, n)
    return {"test_loss": loss, "perplexity": math.exp(min(10, loss))}
