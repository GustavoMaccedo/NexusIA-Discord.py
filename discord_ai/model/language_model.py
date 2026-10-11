from __future__ import annotations

import torch
from torch import nn

from .config import ModelConfig
from .embeddings import TokenPosEmbedding
from .initialization import init_weights_autoral
from .transformer_block import TransformerBlock


class GPTModel(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.emb = TokenPosEmbedding(
            config.vocab_size, config.d_model, config.max_seq, config.dropout
        )
        self.blocks = nn.ModuleList(
            [
                TransformerBlock(config.d_model, config.n_head, config.d_ff, config.dropout)
                for _ in range(config.n_layer)
            ]
        )
        self.ln_f = nn.LayerNorm(config.d_model)
        self.head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        self.apply(init_weights_autoral)

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        x = self.emb(ids)
        for blk in self.blocks:
            x = blk(x)
        return self.head(self.ln_f(x))

    def num_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


def causal_lm_loss(
    logits: torch.Tensor, targets: torch.Tensor, ignore_index: int = -100
) -> torch.Tensor:
    import torch.nn.functional as F

    return F.cross_entropy(
        logits[:, :-1].reshape(-1, logits.size(-1)),
        targets[:, 1:].reshape(-1),
        ignore_index=ignore_index,
    )
