from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int = 8000
    d_model: int = 256
    n_layer: int = 6
    n_head: int = 4
    d_ff: int = 1024
    max_seq: int = 256
    dropout: float = 0.1
    pad_id: int = 0
    bos_id: int = 1
    eos_id: int = 2
    unk_id: int = 3

    def __post_init__(self) -> None:
        assert self.d_model % self.n_head == 0, "d_model deve ser divisível por n_head"
        assert self.vocab_size > 10, "vocab_size inválido"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> ModelConfig:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def count_params_estimate(self) -> int:

        per_layer = 4 * self.d_model * self.d_model + 2 * self.d_model * self.d_ff
        return (
            self.vocab_size * self.d_model
            + self.n_layer * per_layer
            + self.vocab_size * self.d_model
        )


TINY_CONFIG = ModelConfig()
MICRO_CONFIG = ModelConfig(d_model=128, n_layer=2, n_head=2, d_ff=512)
