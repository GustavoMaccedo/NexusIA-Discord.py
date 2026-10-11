from __future__ import annotations

import math

import torch
import torch.nn.functional as F
from torch import nn


def causal_mask(t: int, device) -> torch.Tensor:

    return torch.tril(torch.ones(t, t, dtype=torch.bool, device=device))


class CausalMultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_head: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_head == 0
        self.n_head = n_head
        self.d_k = d_model // n_head
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out = nn.Linear(d_model, d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, t, c = x.shape
        qkv = self.qkv(x).view(b, t, 3, self.n_head, self.d_k).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_k)
        mask = causal_mask(t, x.device).view(1, 1, t, t)
        scores = scores.masked_fill(~mask, float("-inf"))
        w = F.softmax(scores, dim=-1)
        w = self.drop(w)
        y = (w @ v).transpose(1, 2).contiguous().view(b, t, c)
        return self.out(y)
