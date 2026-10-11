from __future__ import annotations

from ...training.preprocessing import deduplicate, split_train_val_test
from ..storage import repositories as repo


async def build_dataset(limit: int = 1000):
    rows = await repo.pending_examples(limit)
    texts = deduplicate([c for _, c, _ in rows])
    hashes = [h for _, _, h in rows]
    tr, va, te = split_train_val_test(texts or ["<bos><usr>oi<sep><asst>olá<eos>"])
    return {"train": tr, "val": va, "test": te, "hashes": hashes}
