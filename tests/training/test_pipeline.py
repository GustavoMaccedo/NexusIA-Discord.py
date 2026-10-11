from discord_ai.model.tokenizer import CharFallbackTokenizer, NexusiaTokenizer
from discord_ai.training.dataset import ConversationDataset
from discord_ai.training.preprocessing import deduplicate, is_eligible, split_train_val_test


def test_char_tokenizer_roundtrip():
    t = CharFallbackTokenizer()
    assert t.decode(t.encode("Olá!")) == "Olá!"


def test_bpe_train_small(tmp_path):
    f = tmp_path / "c.txt"
    f.write_text("<bos><usr>oi<sep><asst>olá<eos>\n" * 20)
    tok = NexusiaTokenizer.train_bpe([str(f)], vocab_size=100, save_path=str(tmp_path / "tok.json"))
    ids = tok.encode("<bos><usr>oi<sep><asst>")
    assert tok.decode(ids)


def test_filters_and_dedup():
    assert not is_eligible("")[0] and not is_eligible("/admin x")[0]
    assert len(deduplicate(["a b c d e f g h", "a b c d e f g h"])) == 1


def test_split_no_contamination():
    tr, va, te = split_train_val_test([f"ex {i} conteudo suficiente" for i in range(50)])
    assert len(tr) > len(va) and not (set(tr) & set(te))


def test_batches():
    ds = ConversationDataset([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], seq_len=4)
    x, y = ds[0]
    assert len(x) == 4 and len(y) == 4
