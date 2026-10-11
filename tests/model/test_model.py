import torch

from discord_ai.model.attention import causal_mask
from discord_ai.model.config import ModelConfig
from discord_ai.model.initialization import verify_random_init
from discord_ai.model.language_model import GPTModel, causal_lm_loss


def test_random_init_and_trainable():
    m = GPTModel(ModelConfig(vocab_size=256, d_model=64, n_layer=2, n_head=2, d_ff=128, max_seq=32))
    v = verify_random_init(m)
    assert v["trainable"] > 0 and not v["all_constant"]


def test_no_external_checkpoint():
    import pathlib

    assert not pathlib.Path("checkpoints/external").exists()


def test_causal_mask():
    mk = causal_mask(4, "cpu")
    assert mk[0, 1] == False and mk[1, 0] == True and mk[2, 2] == True


def test_loss_and_backward_updates():
    m = GPTModel(ModelConfig(vocab_size=128, d_model=32, n_layer=1, n_head=2, d_ff=64, max_seq=16))
    opt = torch.optim.AdamW(m.parameters(), lr=1e-3)
    xb = torch.randint(0, 128, (2, 8))
    before = [p.clone() for p in m.parameters()]
    loss = causal_lm_loss(m(xb), xb)
    loss.backward()
    opt.step()
    assert any(not torch.equal(a, b) for a, b in zip(before, m.parameters()))


def test_overfit_loss_decreases():
    torch.manual_seed(0)
    m = GPTModel(ModelConfig(vocab_size=64, d_model=32, n_layer=2, n_head=2, d_ff=64, max_seq=16))
    opt = torch.optim.AdamW(m.parameters(), lr=3e-3)
    xb = torch.randint(0, 64, (4, 12))
    l0 = causal_lm_loss(m(xb), xb).item()
    for _ in range(20):
        opt.zero_grad()
        causal_lm_loss(m(xb), xb).backward()
        opt.step()
    l1 = causal_lm_loss(m(xb), xb).item()
    assert l1 < l0
