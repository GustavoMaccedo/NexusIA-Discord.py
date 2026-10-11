from __future__ import annotations

from ..model.tokenizer import NexusiaTokenizer


def train_tokenizer_from_dir(corpus_dir: str, out_path: str, vocab_size: int = 8000) -> str:
    from pathlib import Path

    files = [str(p) for p in sorted(Path(corpus_dir).glob("*.txt"))]
    assert files, f"sem corpus em {corpus_dir}"
    NexusiaTokenizer.train_bpe(files, vocab_size=vocab_size, save_path=out_path)
    return out_path
