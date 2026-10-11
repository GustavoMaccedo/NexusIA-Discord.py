from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_checkpoint(
    model,
    optimizer=None,
    scheduler=None,
    config: dict | None = None,
    tokenizer_path: str | None = None,
    dataset_id: str = "unknown",
    metrics: dict | None = None,
    out_dir: str = "checkpoints/active",
    code_version: str = "0.1.0",
) -> str:
    import torch

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / ".tmp_ckpt.pt"
    torch.save(
        {
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict() if optimizer else None,
            "scheduler_state": scheduler.state_dict() if scheduler else None,
            "config": config or {},
        },
        tmp,
    )
    final = out / "model.pt"
    os.replace(tmp, final)
    manifest = {
        "origin": "nexusia-autoral",
        "external_pretrained": False,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset_id": dataset_id,
        "metrics": metrics or {},
        "code_version": code_version,
        "model_sha256": sha256_file(str(final)),
        "tokenizer_sha256": sha256_file(tokenizer_path)
        if tokenizer_path and Path(tokenizer_path).exists()
        else None,
        "config": config or {},
    }
    (out / "meta.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return str(final)


def load_checkpoint(
    model, path: str, optimizer=None, scheduler=None, strict_config: dict | None = None
) -> dict:
    import torch

    ckpt = torch.load(path, map_location="cpu")
    if strict_config and ckpt.get("config"):
        for k, v in strict_config.items():
            assert ckpt["config"].get(k) == v, f"config mismatch em {k}"
    model.load_state_dict(ckpt["model_state"])
    if optimizer and ckpt.get("optimizer_state"):
        optimizer.load_state_dict(ckpt["optimizer_state"])
    if scheduler and ckpt.get("scheduler_state"):
        scheduler.load_state_dict(ckpt["scheduler_state"])
    return ckpt


def verify_provenance(meta_path: str) -> dict:
    m = json.loads(Path(meta_path).read_text())
    assert m.get("origin") == "nexusia-autoral", "checkpoint sem origem autoral"
    assert m.get("external_pretrained") is False, "checkpoint externo rejeitado"
    return m
