from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from ..core.errors import TrainingBusy

_lock = Path("./checkpoints/.training.lock")


def _lock_vivo() -> bool:
    try:
        pid = int(_lock.read_text().strip().split()[0])
        os.kill(pid, 0)
        return True
    except Exception:  # noqa — lock ausente/inválido/processo morto = livre
        return False


def start_training_subprocess(extra: list[str] | None = None) -> int:
    if _lock_vivo():
        raise TrainingBusy("treinamento já em andamento")
    _lock.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")

    cmd = [
        sys.executable,
        "scripts/train_initial_model.py",
        "--out",
        f"checkpoints/candidates/manual-{stamp}",
        "--epochs",
        "1",
        "--dataset-id",
        f"manual-{stamp}",
    ] + (extra or [])
    p = subprocess.Popen(cmd)
    _lock.write_text(str(p.pid))
    return p.pid


def finish_training_lock(pid: int) -> None:
    try:
        if _lock.read_text().strip().split()[0] == str(pid):
            _lock.unlink()
    except FileNotFoundError:
        pass
