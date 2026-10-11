from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path

from ..core.config import settings
from ..core.errors import ModelNotLoaded

TIMEOUT_S = 120
TIME_BUDGET_S = 100
CTX_TOKENS = 128

_model = None
_cfg = None
_tok = None
_lock = asyncio.Semaphore(2)


def _load():
    global _model, _cfg, _tok
    import json

    import torch

    torch.set_num_threads(max(1, os.cpu_count() or 4))
    from discord_ai.model.config import ModelConfig
    from discord_ai.model.language_model import GPTModel

    md = Path(settings.MODEL_DIRECTORY)
    meta = json.loads((md / "meta.json").read_text())
    _cfg = ModelConfig.from_dict(meta["config"])
    _model = GPTModel(_cfg)
    from discord_ai.model.checkpoint import load_checkpoint

    load_checkpoint(_model, str(md / "model.pt"))
    _model.eval()
    with torch.no_grad():
        _model(torch.tensor([[1, 2, 3]], dtype=torch.long))
    tp = Path(settings.TOKENIZER_PATH)
    if tp.exists():
        try:
            from discord_ai.model.tokenizer import NexusiaTokenizer

            _tok = NexusiaTokenizer.load(str(tp))
            if _tok.vocab_size != _cfg.vocab_size:
                raise RuntimeError(
                    f"tokenizer vocab {_tok.vocab_size} != modelo {_cfg.vocab_size} "
                    "(par trocado? restaure o backup)"
                )
        except Exception as e:  # noqa — sem par válido, sem inferência
            _tok = None
            raise RuntimeError(f"tokenizador inválido: {e}")


async def generate_reply(prompt: str, max_attempts: int = 3) -> dict:

    if _model is None:
        try:
            _load()
        except Exception as e:  # noqa
            raise ModelNotLoaded(f"modelo ativo indisponível: {e}")
    async with _lock:
        t0 = time.time()
        try:
            from discord_ai.model.generation import generate

            if _tok is None:
                return {"text": "[modelo sem tokenizador]", "latency_s": 0.0, "empty": True}
            ids = _tok.encode(f"<bos><usr>{prompt[: settings.MAX_INPUT_TOKENS]}<sep><asst>")[
                -CTX_TOKENS:
            ]
            text = ""
            for temp in (0.8, 1.0, 1.3)[: max(1, max_attempts)]:
                out = await asyncio.wait_for(
                    asyncio.to_thread(
                        generate,
                        _model,
                        ids,
                        settings.MAX_GENERATION_TOKENS,
                        temp,
                        50,
                        0.95,
                        _cfg.eos_id,
                        min(_cfg.max_seq, CTX_TOKENS + settings.MAX_GENERATION_TOKENS),
                        "cpu",
                        TIME_BUDGET_S,
                        8,
                        5,
                    ),
                    timeout=TIMEOUT_S,
                )
                text = _tok.decode(out[len(ids) :]).strip()
                if text:
                    break
            return {"text": text[:1900], "latency_s": round(time.time() - t0, 2), "empty": not text}
        except TimeoutError:
            return {
                "text": "Modelo demorou além do limite; tente uma mensagem mais curta.",
                "latency_s": TIMEOUT_S,
                "empty": True,
            }
