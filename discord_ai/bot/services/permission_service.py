from __future__ import annotations

from ..core.config import settings
from ..core.errors import IngestionDisabled, UnauthorizedGuild


def guild_allowed(guild_id: str | None) -> bool:
    if not settings.GUILD_ALLOWLIST:
        return True
    return str(guild_id) in settings.guild_allow


def require_ingestion(guild_id: str | None) -> None:
    if not settings.DISCORD_TRAINING_INGESTION_ENABLED:
        raise IngestionDisabled("ingestão desabilitada (DISCORD_TRAINING_INGESTION_ENABLED=false)")
    if not guild_allowed(guild_id):
        raise UnauthorizedGuild("guild fora da allowlist")
