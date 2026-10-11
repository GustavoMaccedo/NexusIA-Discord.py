from discord_ai.bot.core.client import build_bot
from discord_ai.training.promotion import promotion_decision


def test_reject_worse_candidate():
    ok, _ = promotion_decision({"val_loss": 5.0}, {"val_loss": 2.0})
    assert ok is False


def test_promote_first_version():
    ok, _ = promotion_decision({"val_loss": 5.0}, None)
    assert ok is True


def test_bot_builds_with_minimal_intents():
    b = build_bot()
    assert b.intents.guilds and b.intents.messages


def test_training_lock_segura_segundo_disparo(tmp_path, monkeypatch):
    import os

    from discord_ai.bot.core import errors
    from discord_ai.bot.services import training_service as ts

    monkeypatch.setattr(ts, "_lock", tmp_path / "t.lock")
    ts._lock.write_text(str(os.getpid()))
    try:
        ts.start_training_subprocess(["--help"])
        raise AssertionError("deveria travar")
    except errors.TrainingBusy:
        pass
    ts._lock.write_text("99999999")
    assert ts._lock_vivo() is False


def test_training_service_mira_candidatos_e_nao_o_active(tmp_path, monkeypatch):
    from discord_ai.bot.services import training_service as ts

    monkeypatch.setattr(ts, "_lock", tmp_path / "t.lock")
    cmds = []

    class FakeP:
        pid = 12345

    monkeypatch.setattr(ts.subprocess, "Popen", lambda cmd: (cmds.append(cmd), FakeP())[1])
    ts.start_training_subprocess()
    cmd = cmds[0]
    assert "checkpoints/active" not in " ".join(cmd)
    assert any("checkpoints/candidates/manual-" in c for c in cmd)
