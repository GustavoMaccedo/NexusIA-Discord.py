import torch

from discord_ai.model.checkpoint import load_checkpoint, save_checkpoint, verify_provenance
from discord_ai.model.config import ModelConfig
from discord_ai.model.generation import detect_degeneration, generate
from discord_ai.model.language_model import GPTModel


def test_checkpoint_roundtrip(tmp_path):
    cfg = ModelConfig(
        vocab_size=128, d_model=32, n_layer=1, n_head=2, d_ff=64, max_seq=16
    ).to_dict()
    m = GPTModel(ModelConfig.from_dict(cfg))
    save_checkpoint(m, None, None, cfg, None, "t", {"val_loss": 1.0}, str(tmp_path))
    assert (tmp_path / "model.pt").exists()
    assert verify_provenance(str(tmp_path / "meta.json"))["external_pretrained"] is False
    m2 = GPTModel(ModelConfig.from_dict(cfg))
    load_checkpoint(m2, str(tmp_path / "model.pt"))
    assert torch.equal(
        torch.cat([p.flatten() for p in m.parameters()]),
        torch.cat([p.flatten() for p in m2.parameters()]),
    )


def test_generation_limits():
    m = GPTModel(ModelConfig(vocab_size=64, d_model=32, n_layer=1, n_head=2, d_ff=64, max_seq=16))
    out = generate(m, [1, 5, 6], max_new_tokens=10)
    assert len(out) <= 13
    assert "empty" in detect_degeneration("")


def test_generation_respeita_time_budget():
    m = GPTModel(ModelConfig(vocab_size=64, d_model=32, n_layer=1, n_head=2, d_ff=64, max_seq=16))
    out = generate(m, [1, 5, 6], max_new_tokens=1000, time_budget_s=0.0)
    assert len(out) == 3


def test_generation_para_em_loop_de_repeticao():
    class Loopless(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.n = 0

        def forward(self, x):
            import torch as t

            b, tt = x.shape
            logits = t.full((b, tt, 64), float("-inf"))
            tok = 10 + (self.n % 8)
            self.n += 1
            logits[:, :, tok] = 0.0
            return logits

    out = generate(Loopless(), [1, 5, 6], max_new_tokens=200, temperature=0.0)
    assert len(out) < 3 + 200


def test_generation_min_new_tokens_suprime_eos():
    class EosFirst(torch.nn.Module):
        def forward(self, x):
            import torch as t

            b, tt = x.shape
            logits = t.full((b, tt, 64), float("-inf"))
            logits[:, :, 2] = 0.0
            logits[:, :, 10] = -1.0
            return logits

    out = generate(EosFirst(), [1, 5, 6], max_new_tokens=10, temperature=0.0, min_new_tokens=3)
    gen = out[3:]
    assert len(gen) >= 3 and gen[0] != 2 and gen[1] != 2 and gen[2] != 2
    out_sem_min = generate(EosFirst(), [1, 5, 6], max_new_tokens=10, temperature=0.0)
    assert out_sem_min[3:] == [2]
