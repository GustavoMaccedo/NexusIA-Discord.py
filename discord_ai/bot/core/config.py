from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DISCORD_TOKEN: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./nexusia.db"
    MODEL_DIRECTORY: str = "./checkpoints/active"
    CANDIDATE_DIRECTORY: str = "./checkpoints/candidates"
    TOKENIZER_PATH: str = "./checkpoints/active/tokenizer.json"
    TRAINING_DATA_DIRECTORY: str = "./datasets/prepared"
    TRAINING_ENABLED: bool = False
    DISCORD_TRAINING_INGESTION_ENABLED: bool = False
    LOG_LEVEL: str = "INFO"
    MAX_GENERATION_TOKENS: int = 128
    MAX_INPUT_TOKENS: int = 256
    TRAINING_MAX_RAM_MB: int = 1500
    TRAINING_INTERVAL: int = 3600
    GUILD_ALLOWLIST: str = ""

    CHAT_CHANNEL_ID: str = ""

    TRAINER_BOT_IDS: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def guild_allow(self) -> set[str]:
        return {g.strip() for g in self.GUILD_ALLOWLIST.split(",") if g.strip()}

    @property
    def chat_channels(self) -> set[str]:
        return {c.strip() for c in self.CHAT_CHANNEL_ID.split(",") if c.strip()}

    @property
    def trainer_bots(self) -> set[str]:
        return {b.strip() for b in self.TRAINER_BOT_IDS.split(",") if b.strip()}


settings = Settings()
