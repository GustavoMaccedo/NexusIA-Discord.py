from __future__ import annotations

import torch
from torch.utils.data import Dataset


class ConversationDataset(Dataset):
    def __init__(self, tokenized: list[list[int]], seq_len: int = 128, pad_id: int = 0):
        self.seq_len = seq_len
        self.pad_id = pad_id
        self.samples: list[list[int]] = []
        for ids in tokenized:
            for i in range(0, len(ids), seq_len):
                chunk = ids[i : i + seq_len + 1]
                if len(chunk) < min(8, seq_len + 1):
                    continue
                if len(chunk) < seq_len + 1:
                    chunk = chunk + [pad_id] * (seq_len + 1 - len(chunk))
                self.samples.append(chunk)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        s = torch.tensor(self.samples[i], dtype=torch.long)
        return s[:-1], s[1:]
