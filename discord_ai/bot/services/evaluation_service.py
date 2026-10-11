from __future__ import annotations

from ...training.promotion import promotion_decision


def judge(candidate: dict, active: dict | None) -> dict:
    ok, reason = promotion_decision(candidate, active)
    return {"approved": ok, "reason": reason}
