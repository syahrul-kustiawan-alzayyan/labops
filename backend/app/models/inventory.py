import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey, Text, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Component(Base):
    __tablename__ = "components"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(50))
    is_consumable: Mapped[bool] = mapped_column(Boolean, default=False)
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Unit(Base):
    __tablename__ = "units"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    component_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("components.id"))
    serial_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    brand_model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lab_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labs.id"))
    placement: Mapped[str | None] = mapped_column(String(200), nullable=True)
    acquired_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    funding_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ownership: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Siap Pakai")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class UnitConditionHistory(Base):
    __tablename__ = "unit_condition_history"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id"))
    old_status: Mapped[str] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    changed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

class UnitVerification(Base):
    __tablename__ = "unit_verifications"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id"))
    result: Mapped[str] = mapped_column(String(10))  # pass/fail
    failed_items: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

class Checklist(Base):
    __tablename__ = "checklists"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lab_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labs.id"))
    date: Mapped[date] = mapped_column(Date)
    items: Mapped[list] = mapped_column(JSON)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    conclusion: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

class Consumable(Base):
    __tablename__ = "consumables"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    component_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("components.id"))
    lab_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labs.id"))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Lab(Base):
    __tablename__ = "labs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(String(50), unique=True)
    aliases: Mapped[list | None] = mapped_column(JSON, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=30)
    facilities: Mapped[list | None] = mapped_column(JSON, nullable=True)
    capabilities: Mapped[list | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="aktif")