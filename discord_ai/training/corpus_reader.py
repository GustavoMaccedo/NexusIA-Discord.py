from __future__ import annotations

from pathlib import Path


def read_corpus_files(paths: list[str], encoding: str = "utf-8") -> list[str]:
    texts = []
    for p in paths:
        texts.extend(Path(p).read_text(encoding=encoding).splitlines())
    return [t for t in texts if t.strip()]


def corpus_from_dir(d: str, pattern: str = "*.txt") -> list[str]:
    files = sorted(Path(d).glob(pattern))
    return read_corpus_files([str(f) for f in files])
