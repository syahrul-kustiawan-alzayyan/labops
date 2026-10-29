import uuid
from datetime import datetime, timezone, date, time
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Time, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(20))  # fakultas/prodi
    platform: Mapped[str] = mapped_column(String(50))
    prodi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    audience: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ideal_posting_time: Mapped[time | None] = mapped_column(Time, nullable=True)

class ContentIdea(Base):
    __tablename__ = "content_ideas"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(300))
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_account_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("social_accounts.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Content(Base):
    __tablename__ = "contents"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(300))
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("social_accounts.id"))
    idea_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_ideas.id"), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    scheduled_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Ide")
    revision_no: Mapped[int] = mapped_column(Integer, default=1)
    parent_content_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("contents.id"), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ContentChecklist(Base):
    __tablename__ = "content_checklists"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contents.id"), unique=True)
    items: Mapped[list] = mapped_column(JSON)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class ContentAsset(Base):
    __tablename__ = "content_assets"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contents.id"))
    type: Mapped[str] = mapped_column(String(20))  # image/video/document
    version: Mapped[int] = mapped_column(Integer, default=1)
    storage_path: Mapped[str] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Reminder(Base):
    __tablename__ = "reminders"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[uuid.UUID] = mapped_column()
    kind: Mapped[str] = mapped_column(String(20))  # H-3/H-1/H-0/overdue
    send_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)