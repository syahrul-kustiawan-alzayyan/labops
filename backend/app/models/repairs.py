import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Vendor(Base):
    __tablename__ = "vendors"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    service_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    performance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    number: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    reporter: Mapped[str | None] = mapped_column(String(200), nullable=True)
    severity: Mapped[str] = mapped_column(String(20))  # Ringan/Sedang/Berat/Kritis
    impact: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[str] = mapped_column(String(10))  # PRI-1..PRI-4
    status: Mapped[str] = mapped_column(String(30), default="Dilaporkan")
    kronologi: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_remediation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    triaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    closed_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

class TicketAction(Base):
    __tablename__ = "ticket_actions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id"))
    type: Mapped[str] = mapped_column(String(20))  # internal/vendor
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    action: Mapped[str | None] = mapped_column(Text, nullable=True)
    sparepart: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vendors.id"), nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))