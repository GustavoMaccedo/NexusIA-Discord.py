from __future__ import annotations

import torch
from torch import nn


class TokenPosEmbedding(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, max_seq: int, dropout: float = 0.1):
        super().__init__()
        self.tok = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Embedding(max_seq, d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        b, t = ids.shape
        pos = torch.arange(t, device=ids.device).unsqueeze(0).expand(b, t)
        return self.drop(self.tok(ids) + self.pos(pos))
