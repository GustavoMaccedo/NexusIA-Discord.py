from __future__ import annotations

import discord
from discord.ext import commands

from .logging_config import get_logger

log = get_logger("nexusia.client")


def build_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True

    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    return bot
