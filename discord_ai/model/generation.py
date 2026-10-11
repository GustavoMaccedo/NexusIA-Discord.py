from __future__ import annotations

import time

import torch
import torch.nn.functional as F


def _top_k_top_p(logits: torch.Tensor, top_k: int = 50, top_p: float = 0.95) -> torch.Tensor:
    if top_k > 0:
        v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
        logits = torch.where(
            logits < v[:, [-1]], torch.tensor(float("-inf"), device=logits.device), logits
        )
    if top_p < 1.0:
        probs = F.softmax(logits, dim=-1)
        sorted_probs, sorted_idx = torch.sort(probs, descending=True)
        cumsum = torch.cumsum(sorted_probs, dim=-1)
        mask = cumsum - sorted_probs > top_p
        sorted_probs[mask] = 0.0
        sorted_probs = sorted_probs / sorted_probs.sum(dim=-1, keepdim=True)
        logits = torch.log(sorted_probs.clamp_min(1e-12)).gather(-1, sorted_idx.argsort(-1))
    return logits


@torch.no_grad()
def generate(
    model,
    ids: list[int],
    max_new_tokens: int = 64,
    temperature: float = 0.8,
    top_k: int = 50,
    top_p: float = 0.95,
    eos_id: int = 2,
    max_seq: int = 256,
    device: str = "cpu",
    time_budget_s: float | None = None,
    loop_window: int = 8,
    min_new_tokens: int = 0,
) -> list[int]:

    model.eval()
    out = list(ids)
    gen: list[int] = []
    repeats = 0
    t0 = time.monotonic()
    for _ in range(max_new_tokens):
        if time_budget_s is not None and time.monotonic() - t0 > time_budget_s:
            break
        ctx = out[-max_seq:]
        x = torch.tensor([ctx], dtype=torch.long, device=device)
        logits = model(x)[0, -1, :]
        if len(gen) < min_new_tokens and eos_id < logits.numel():
            logits = logits.clone()
            logits[eos_id] = float("-inf")
        if temperature <= 0:
            nxt = int(torch.argmax(logits))
        else:
            logits = _top_k_top_p((logits / temperature).unsqueeze(0), top_k, top_p)[0]
            nxt = int(torch.multinomial(F.softmax(logits, dim=-1), 1))
        out.append(nxt)
        gen.append(nxt)
        if nxt == eos_id:
            break
        if (
            len(gen) >= 2 * loop_window
            and gen[-loop_window:] == gen[-2 * loop_window : -loop_window]
        ):
            repeats += 1
            if repeats >= 2:
                break
        else:
            repeats = 0
    return out


def detect_degeneration(text: str) -> list[str]:
    issues = []
    if not text.strip():
        issues.append("empty")
    words = text.split()
    if len(words) > 10 and len(set(words)) / len(words) < 0.3:
        issues.append("repetition")
    for tok in ("<bos>", "<eos>", "<usr>", "<asst>", "<sep>"):
        if tok in text:
            issues.append("special_leak")
            break
    if len(text) > 1900:
        issues.append("too_long")
    return issues
