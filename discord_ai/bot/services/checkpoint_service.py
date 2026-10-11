from __future__ import annotations

from pathlib import Path

from ...model.checkpoint import verify_provenance
from ..core.config import settings


def active_info() -> dict:
    md = Path(settings.MODEL_DIRECTORY)
    meta = md / "meta.json"
    if not meta.exists():
        return {"loaded": False}
    m = verify_provenance(str(meta))
    return {"loaded": True, **m}
