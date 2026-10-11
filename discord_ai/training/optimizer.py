from __future__ import annotations

import torch


def build_optimizer(model, lr: float = 3e-4, weight_decay: float = 0.01):
    return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)


def build_scheduler(optimizer, total_steps: int):
    return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, total_steps))
