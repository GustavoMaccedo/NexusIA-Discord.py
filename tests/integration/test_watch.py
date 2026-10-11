from __future__ import annotations

import asyncio
import types

from discord_ai.bot.cogs import watch as watch_mod
from discord_ai.bot.core.config import settings
from discord_ai.training import pair_builder as pb


def _msg(
    *,
    channel_id=123,
    content="texto de conversa válido aqui",
    bot=False,
    guild_id=42,
    reference=None,
    fetch=None,
):
    channel = types.SimpleNamespace(id=channel_id)
    if fetch is not None:
        channel.fetch_message = fetch
    return types.SimpleNamespace(
        channel=channel,
        author=types.SimpleNamespace(id=7, bot=bot),
        content=content,
        guild=None if guild_id is None else types.SimpleNamespace(id=guild_id),
        reference=reference,
    )


def _run(coro):
    return asyncio.run(coro)


def test_build_pair_formato_exato():
    line = pb.build_pair("olá, como você está hoje?", "estou bem, obrigado por perguntar!")
    assert (
        line
        == "<bos><usr>olá, como você está hoje?<sep><asst>estou bem, obrigado por perguntar!<eos>"
    )


def test_build_pair_lado_inelegivel_retorna_none():
    assert pb.build_pair("oi", "resposta longa o suficiente aqui") is None
    assert pb.build_pair("pergunta longa o suficiente aqui", "x") is None
    assert pb.build_pair("/admin purge tudo isso aqui agora", "resposta válida aqui sim") is None
    assert pb.build_pair("a" * 601 + " texto extra aqui", "resposta válida aqui sim") is None
    assert pb.build_pair(None, "resposta válida aqui sim") is None


def test_build_single_formato_e_comando_admin_none():

    assert (
        pb.build_single("observação interessante sobre o jogo")
        == "<bos><usr>observação interessante sobre o jogo<eos>"
    )
    assert pb.build_single("/admin purge tudo isso aqui agora") is None
    assert pb.build_single("curto") is None
    assert pb.build_single("") is None


def _patch_settings(channel="123"):
    old = (
        settings.CHAT_CHANNEL_ID,
        settings.DISCORD_TRAINING_INGESTION_ENABLED,
        settings.GUILD_ALLOWLIST,
    )
    settings.CHAT_CHANNEL_ID = channel
    settings.DISCORD_TRAINING_INGESTION_ENABLED = True
    settings.GUILD_ALLOWLIST = ""
    return old


def _restore_settings(old):
    (
        settings.CHAT_CHANNEL_ID,
        settings.DISCORD_TRAINING_INGESTION_ENABLED,
        settings.GUILD_ALLOWLIST,
    ) = old


def test_listener_ignora_autor_bot():
    import discord_ai.bot.storage.repositories as repo

    calls = []

    async def fake_add(*a, **k):
        calls.append((a, k))
        return True

    orig = repo.add_example
    repo.add_example = fake_add
    old = _patch_settings()
    try:
        _run(watch_mod.Watch(types.SimpleNamespace()).on_watch(_msg(bot=True)))
    finally:
        repo.add_example = orig
        _restore_settings(old)
    assert calls == []


def test_listener_ignora_canal_fora_da_lista():
    import discord_ai.bot.storage.repositories as repo

    calls = []

    async def fake_add(*a, **k):
        calls.append((a, k))
        return True

    orig = repo.add_example
    repo.add_example = fake_add
    old = _patch_settings(channel="123")
    try:
        _run(watch_mod.Watch(types.SimpleNamespace()).on_watch(_msg(channel_id=999)))
    finally:
        repo.add_example = orig
        _restore_settings(old)
    assert calls == []


def test_listener_ingere_single_em_canal_certo():
    import discord_ai.bot.storage.repositories as repo

    calls = []

    async def fake_add(gh, content, ch, scope="guild"):
        calls.append((gh, content, ch, scope))
        return True

    orig = repo.add_example
    repo.add_example = fake_add
    old = _patch_settings()
    try:
        _run(
            watch_mod.Watch(types.SimpleNamespace()).on_watch(
                _msg(content="conversa normal entre pessoas aqui")
            )
        )
    finally:
        repo.add_example = orig
        _restore_settings(old)
    assert len(calls) == 1
    assert calls[0][1] == "<bos><usr>conversa normal entre pessoas aqui<eos>"
    assert calls[0][3] == "watch"


def test_reply_com_pai_valido_chama_add_example_scope_reply_pair():
    import discord_ai.bot.storage.repositories as repo

    calls = []

    async def fake_add(gh, content, ch, scope="guild"):
        calls.append((gh, content, ch, scope))
        return True

    async def fake_fetch(mid):
        assert mid == 111
        return types.SimpleNamespace(
            author=types.SimpleNamespace(bot=False),
            content="você viu o jogo de ontem à noite?",
        )

    orig = repo.add_example
    repo.add_example = fake_add
    old = _patch_settings()
    try:
        _run(
            watch_mod.Watch(types.SimpleNamespace()).on_watch(
                _msg(
                    content="vi sim, foi um jogão do começo ao fim",
                    reference=types.SimpleNamespace(message_id=111),
                    fetch=fake_fetch,
                )
            )
        )
    finally:
        repo.add_example = orig
        _restore_settings(old)
    assert len(calls) == 1
    _gh, content, _ch, scope = calls[0]
    assert scope == "reply-pair"
    assert content == (
        "<bos><usr>você viu o jogo de ontem à noite?"
        "<sep><asst>vi sim, foi um jogão do começo ao fim<eos>"
    )


def test_pai_deletado_fetch_lanca_cai_para_single():
    import discord_ai.bot.storage.repositories as repo

    calls = []

    async def fake_add(gh, content, ch, scope="guild"):
        calls.append((gh, content, ch, scope))
        return True

    async def boom_fetch(mid):
        raise RuntimeError("NotFound simulado: mensagem deletada")

    orig = repo.add_example
    repo.add_example = fake_add
    old = _patch_settings()
    try:
        _run(
            watch_mod.Watch(types.SimpleNamespace()).on_watch(
                _msg(
                    content="mensagem órfã que continua válida aqui",
                    reference=types.SimpleNamespace(message_id=222),
                    fetch=boom_fetch,
                )
            )
        )
    finally:
        repo.add_example = orig
        _restore_settings(old)
    assert len(calls) == 1
    assert calls[0][1] == "<bos><usr>mensagem órfã que continua válida aqui<eos>"
    assert calls[0][3] == "watch"


def test_dm_usa_guild_id_dm_e_nunca_derruba_loop():
    import hashlib

    import discord_ai.bot.storage.repositories as repo

    calls = []

    async def fake_add(gh, content, ch, scope="guild"):
        calls.append((gh, content, ch, scope))
        return True

    orig = repo.add_example
    repo.add_example = fake_add
    old = _patch_settings()
    try:
        _run(
            watch_mod.Watch(types.SimpleNamespace()).on_watch(
                _msg(guild_id=None, content="conversa vinda de mensagem direta aqui")
            )
        )
    finally:
        repo.add_example = orig
        _restore_settings(old)
    assert len(calls) == 1
    assert calls[0][0] == hashlib.sha256(b"guild:dm:123").hexdigest()[:16]
    assert calls[0][1] == "<bos><usr>conversa vinda de mensagem direta aqui<eos>"
    assert calls[0][3] == "watch"
