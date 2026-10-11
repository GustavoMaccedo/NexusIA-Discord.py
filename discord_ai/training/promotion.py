from __future__ import annotations

import shutil
from pathlib import Path


def promotion_decision(
    candidate_metrics: dict, active_metrics: dict | None, max_regression: float = 0.05
) -> tuple[bool, str]:
    if active_metrics is None:
        return True, "sem ativo: promover"
    cand, act = candidate_metrics.get("val_loss", 9e9), active_metrics.get("val_loss", 9e9)
    if cand <= act * (1 + max_regression):
        return True, f"candidato {cand:.3f} vs ativo {act:.3f}: aprovar"
    return False, f"candidato {cand:.3f} pior que ativo {act:.3f}: rejeitar"


def promote_candidate(candidate_dir: str, active_dir: str) -> None:
    src, dst = Path(candidate_dir), Path(active_dir)
    dst.mkdir(parents=True, exist_ok=True)
    for f in ("model.pt", "meta.json", "history.json", "tokenizer.json"):
        if (src / f).exists():
            shutil.copy2(src / f, dst / f)


def rollback_to(previous_dir: str, active_dir: str) -> None:
    promote_candidate(previous_dir, active_dir)
