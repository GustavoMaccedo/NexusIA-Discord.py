from __future__ import annotations

from pathlib import Path

SPECIALS = ["<pad>", "<bos>", "<eos>", "<unk>", "<usr>", "<asst>", "<sep>"]
BOS, EOS, PAD = "<bos>", "<eos>", "<pad>"


class CharFallbackTokenizer:
    def __init__(self):
        base = (
            [chr(i) for i in range(32, 127)] + [chr(i) for i in range(160, 256)] + ["\n"] + SPECIALS
        )
        chars = sorted(set(base))
        self.stoi = {c: i for i, c in enumerate(sorted(set(chars)))}
        self.itos = {i: c for c, i in self.stoi.items()}
        self.vocab_size = len(self.stoi)
        for s, attr in [
            ("<pad>", "pad_id"),
            ("<bos>", "bos_id"),
            ("<eos>", "eos_id"),
            ("<unk>", "unk_id"),
        ]:
            setattr(self, attr, self.stoi[s])

    def encode(self, text: str) -> list[int]:
        return [self.stoi.get(c, self.unk_id) for c in text]

    def decode(self, ids: list[int]) -> str:
        return "".join(self.itos.get(i, "<unk>") for i in ids)


class NexusiaTokenizer:
    def __init__(self, tokenizer=None, specials: list[str] | None = None):
        self.tok = tokenizer
        self.specials = specials or SPECIALS

    @classmethod
    def train_bpe(
        cls, files: list[str], vocab_size: int = 8000, save_path: str = "tokenizer.json"
    ) -> NexusiaTokenizer:
        from tokenizers import Tokenizer
        from tokenizers.decoders import BPEDecoder
        from tokenizers.models import BPE
        from tokenizers.pre_tokenizers import Whitespace
        from tokenizers.trainers import BpeTrainer

        tok = Tokenizer(BPE(unk_token="<unk>"))
        tok.pre_tokenizer = Whitespace()
        tok.decoder = BPEDecoder()
        trainer = BpeTrainer(vocab_size=vocab_size, special_tokens=SPECIALS, show_progress=False)
        tok.train(files, trainer)
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        tok.save(save_path)
        return cls(tok)

    @classmethod
    def train_from_texts(
        cls, texts: list[str], vocab_size: int = 8000, save_path: str = "tokenizer.json"
    ) -> NexusiaTokenizer:
        from tokenizers import Tokenizer
        from tokenizers.decoders import BPEDecoder
        from tokenizers.models import BPE
        from tokenizers.pre_tokenizers import Whitespace
        from tokenizers.trainers import BpeTrainer

        tok = Tokenizer(BPE(unk_token="<unk>"))
        tok.pre_tokenizer = Whitespace()
        tok.decoder = BPEDecoder()
        trainer = BpeTrainer(vocab_size=vocab_size, special_tokens=SPECIALS, show_progress=False)
        tok.train_from_iterator(texts, trainer=trainer)
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        tok.save(save_path)
        return cls(tok)

    @classmethod
    def load(cls, path: str) -> NexusiaTokenizer:
        from tokenizers import Tokenizer

        return cls(Tokenizer.from_file(path))

    def encode(self, text: str) -> list[int]:
        return self.tok.encode(text).ids

    def decode(self, ids: list[int]) -> str:
        return self.tok.decode(ids)

    @property
    def vocab_size(self) -> int:
        return self.tok.get_vocab_size()

    def serialize_dialog(self, user: str, assistant: str | None = None) -> str:
        s = f"<bos><usr>{user}<sep><asst>"
        if assistant is not None:
            s += f"{assistant}<eos>"
        return s
