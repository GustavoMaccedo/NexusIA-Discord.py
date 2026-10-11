from __future__ import annotations

import asyncio
import types

from discord_ai.bot.services import conversation_service as conv


def test_bot_tem_message_content_para_ler_o_canal():
    from discord_ai.bot.core.client import build_bot

    assert build_bot().intents.message_content is True


def test_gate_responde_no_canal_configurado():
    ok, reason = conv.should_auto_reply(1497662958753419330, False, "olá!", {"1497662958753419330"})
    assert (ok, reason) == (True, "ok")


def test_gate_ignora_proprio_bot_e_outros_bots():
    assert (
        conv.should_auto_reply(1497662958753419330, True, "olá!", {"1497662958753419330"})[0]
        is False
    )


def test_gate_responde_trainer_configurado_e_so_ele():
    cfg, trainers = {"1497662958753419330"}, {"1558832243546521742"}
    ok, reason = conv.should_auto_reply(
        1497662958753419330,
        True,
        "🧪 Treino: olá!",
        cfg,
        author_id=1558832243546521742,
        trainers=trainers,
    )
    assert (ok, reason) == (True, "ok")
    assert (
        conv.should_auto_reply(
            1497662958753419330, True, "oi", cfg, author_id=999, trainers=trainers
        )[0]
        is False
    )


def test_gate_ignora_outro_canal_e_sem_config():
    assert conv.should_auto_reply(999, False, "olá!", {"1497662958753419330"}) == (
        False,
        "other_channel",
    )
    assert conv.should_auto_reply(1497662958753419330, False, "olá!", set())[0] is False


def test_gate_ignora_vazio_e_prefixo_de_comando():
    cfg = {"1497662958753419330"}
    assert conv.should_auto_reply(1497662958753419330, False, "   ", cfg) == (False, "empty")
    assert conv.should_auto_reply(1497662958753419330, False, "!ajuda", cfg) == (
        False,
        "command_prefix",
    )


def test_sessao_isolada_por_canal_e_usuario():
    assert conv.channel_session(1, 2) != conv.channel_session(1, 3)
    assert conv.channel_session(1, 2) != conv.channel_session(9, 2)


def test_listener_nao_derruba_loop_quando_modelo_falha():
    from discord_ai.bot.cogs import chat as chat_mod

    async def boom(prompt):
        raise RuntimeError("sem modelo")

    replies = []

    async def fake_reply(text, mention_author=False):
        replies.append(text)

    class FakeTyping:
        async def __aenter__(self): ...
        async def __aexit__(self, *a): ...

    msg = types.SimpleNamespace(
        channel=types.SimpleNamespace(id=1497662958753419330, typing=lambda: FakeTyping()),
        author=types.SimpleNamespace(id=7, bot=False),
        content="oi",
        guild=types.SimpleNamespace(id=42),
        reply=fake_reply,
    )
    cog = chat_mod.Chat(types.SimpleNamespace(command_prefix="!"))

    from discord_ai.bot.core.config import settings

    old_chan = settings.CHAT_CHANNEL_ID
    settings.CHAT_CHANNEL_ID = "1497662958753419330"
    import discord_ai.bot.services.inference_service as inf

    orig = inf.generate_reply
    inf.generate_reply = boom
    try:
        asyncio.run(cog.chat_no_canal(msg))
    finally:
        inf.generate_reply = orig
        settings.CHAT_CHANNEL_ID = old_chan
    assert replies and "indisponível" in replies[0]
