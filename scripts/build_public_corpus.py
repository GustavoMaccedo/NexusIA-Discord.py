#!/usr/bin/env python3
import random
from pathlib import Path

import pandas as pd

from discord_ai.training.preprocessing import is_eligible, text_hash


def clean(t: str, limit: int = 1200) -> str:
    return " ".join(str(t).split())[:limit]


def main() -> None:
    tr = pd.read_parquet("data/oasst1_pt/data/train-00000-of-00001.parquet")
    va = pd.read_parquet("data/oasst1_pt/data/validation-00000-of-00001.parquet")
    by_id = {r.message_id: r for r in tr.itertuples()}
    vby_id = {r.message_id: r for r in va.itertuples()}

    def pairs(df, idmap):
        out = []
        for r in df.itertuples():
            if r.role != "assistant" or r.deleted:
                continue
            p = idmap.get(r.parent_id)
            if p is None or p.role != "prompter":
                continue
            q, a = clean(p.text), clean(r.text)
            line = f"<bos><usr>{q}<sep><asst>{a}<eos>"
            ok, _ = is_eligible(line)
            if ok:
                out.append(line)

        seen, uniq = set(), []
        for l in out:
            h = text_hash(l)
            if h not in seen:
                seen.add(h)
                uniq.append(l)
        return uniq

    train_lines = pairs(tr, by_id)
    val_lines = pairs(va, vby_id)
    rng = random.Random(99)
    rng.shuffle(val_lines)
    holdout, _val_rest = (
        val_lines[:200],
        val_lines[200:],
    )
    assert not (set(map(text_hash, train_lines)) & set(map(text_hash, holdout)))

    import json

    with open("data/faquad.json") as f:
        fq = json.load(f)["data"]
    fq_lines = []
    for doc in fq:
        for par in doc["paragraphs"]:
            for qa in par.get("qas", []):
                ans = (qa.get("answers") or [{}])[0].get("text", "")
                line = f"<bos><usr>{clean(qa['question'])}<sep><asst>{clean(ans)}<eos>"
                ok, _ = is_eligible(line)
                if ok:
                    fq_lines.append(line)

    Path("datasets/incoming/public_pt.txt").write_text("\n".join(train_lines + fq_lines) + "\n")
    Path("datasets/evaluation/holdout_oasst.txt").write_text("\n".join(holdout) + "\n")
    print(
        f"public train: oasst={len(train_lines)} faquad={len(fq_lines)} total={len(train_lines) + len(fq_lines)}"
    )
    print(f"holdout oasst: {len(holdout)} (validation nunca no treino)")


if __name__ == "__main__":
    main()
