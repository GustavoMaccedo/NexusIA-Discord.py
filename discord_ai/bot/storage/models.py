from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class GuildConfig(Base):
    __tablename__ = "guild_config"
    guild_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    ingestion_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PrivacySetting(Base):
    __tablename__ = "privacy_setting"
    guild_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    policy_version: Mapped[str] = mapped_column(String(32), default="v1")
    allow_training: Mapped[bool] = mapped_column(Boolean, default=False)


class EligibleExample(Base):
    __tablename__ = "eligible_example"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_hash: Mapped[str] = mapped_column(String(64), index=True)
    content_hash: Mapped[str] = mapped_column(String(32), index=True)
    content: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String(32), default="guild")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DatasetMeta(Base):
    __tablename__ = "dataset_meta"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    n_examples: Mapped[int] = mapped_column(Integer, default=0)
    n_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TrainingRun(Base):
    __tablename__ = "training_run"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    checkpoint: Mapped[str] = mapped_column(String(256), default="")
    status: Mapped[str] = mapped_column(String(16), default="queued")
    train_loss: Mapped[float] = mapped_column(Float, default=0)
    val_loss: Mapped[float] = mapped_column(Float, default=0)


class CheckpointRecord(Base):
    __tablename__ = "checkpoint_record"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    path: Mapped[str] = mapped_column(String(256))
    origin: Mapped[str] = mapped_column(String(32), default="nexusia-autoral")
    val_loss: Mapped[float] = mapped_column(Float, default=0)


class EvalResult(Base):
    __tablename__ = "eval_result"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checkpoint_id: Mapped[str] = mapped_column(String(64), index=True)
    test_loss: Mapped[float] = mapped_column(Float, default=0)
    perplexity: Mapped[float] = mapped_column(Float, default=0)


class Release(Base):
    __tablename__ = "release"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checkpoint_id: Mapped[str] = mapped_column(String(64))
    active: Mapped[bool] = mapped_column(Boolean, default=False)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_hash: Mapped[str] = mapped_column(String(64))
    rating: Mapped[int] = mapped_column(Integer)
    correction: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="pending")


class DeletionRecord(Base):
    __tablename__ = "deletion_record"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_hash: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(String(128), default="")


class AdminLog(Base):
    __tablename__ = "admin_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(String(512), default="")
