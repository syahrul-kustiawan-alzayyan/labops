import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.repairs import Ticket, TicketAction, Vendor
from app.models.inventory import Unit
from app.models.core import ActivityLog
from app.core.errors import NotFoundError, ConflictError

PRIORITY_MATRIX = {
    ("Kritis", True): "PRI-1", ("Kritis", False): "PRI-2",
    ("Berat", True): "PRI-2", ("Berat", False): "PRI-3",
    ("Sedang", True): "PRI-3", ("Sedang", False): "PRI-4",
    ("Ringan", True): "PRI-4", ("Ringan", False): "PRI-4",
}
SLA_REMEDIATION = {"Ringan": 7, "Sedang": 14, "Berat": 30, "Kritis": 3}
SLA_RESPONSE = {"Kritis": 1, "Berat": 1, "Sedang": 2, "Ringan": 3}

class RepairsService:
    def __init__(self, db: AsyncSession, user_id=None):
        self.db = db
        self.user_id = user_id

    async def _audit(self, entity_type, entity_id, action, before=None, after=None, reason=None):
        self.db.add(ActivityLog(actor_id=self.user_id, entity_type=entity_type, entity_id=entity_id,
                                action=action, before_data=before, after_data=after, reason=reason))

    def _next_number(self):
        return f"RPR-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:3].upper()}"

    async def create_ticket(self, data: dict):
        unit_id = data.get("unit_id")
        if unit_id:
            existing = (await self.db.execute(
                select(Ticket).where(Ticket.unit_id == unit_id, Ticket.status.in_(
                    ["Dilaporkan", "Ditriase", "Dalam Perbaikan", "Menunggu Suku Cadang/Vendor", "Selesai Diperbaiki"]))
            )).scalar_one_or_none()
            if existing:
                raise ConflictError("Unit ini sudah punya tiket aktif")
        severity = data["severity"]
        impact = data.get("impact", False)
        priority = PRIORITY_MATRIX.get((severity, impact), "PRI-4")
        resp_days = SLA_RESPONSE.get(severity, 3)
        rem_days = SLA_REMEDIATION.get(severity, 7)
        now = datetime.now(timezone.utc)
        t = Ticket(
            number=self._next_number(),
            unit_id=unit_id,
            reporter=data.get("reporter"),
            severity=severity,
            impact=impact,
            priority=priority,
            kronologi=data.get("kronologi"),
            due_response_at=now + timedelta(days=resp_days),
            due_remediation_at=now + timedelta(days=rem_days),
        )
        self.db.add(t)
        await self.db.commit()
        await self.db.refresh(t)
        await self._audit("ticket", t.id, "create", after={"number": t.number, "priority": priority})
        await self.db.commit()
        return t

    async def list_tickets(self, status=None, priority=None):
        q = select(Ticket)
        if status:
            q = q.where(Ticket.status == status)
        if priority:
            q = q.where(Ticket.priority == priority)
        q = q.order_by(Ticket.created_at.desc())
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def get_ticket(self, ticket_id):
        r = await self.db.execute(select(Ticket).where(Ticket.id == ticket_id))
        t = r.scalar_one_or_none()
        if not t:
            raise NotFoundError("Tiket tidak ditemukan")
        return t

    async def triage(self, ticket_id, result, note):
        t = await self.get_ticket(ticket_id)
        if result == "duplikat" or result == "tidak_valid":
            t.status = "Duplikat" if result == "duplikat" else "Tidak Valid"
            t.closed_reason = note
            t.triaged_at = datetime.now(timezone.utc)
            await self._audit("ticket", t.id, "triage", reason=note)
            await self.db.commit()
            await self.db.refresh(t)
            return t
        t.status = "Ditriase"
        t.triaged_at = datetime.now(timezone.utc)
        # BR-26b: tiket Berat/Kritis memindahkan unit Siap Pakai/Perlu Perhatian -> Rusak
        if t.severity in ("Berat", "Kritis") and t.unit_id:
            from app.models.inventory import Unit
            u = (await self.db.execute(select(Unit).where(Unit.id == t.unit_id))).scalar_one_or_none()
            if u and u.status in ("Siap Pakai", "Perlu Perhatian"):
                old = u.status
                u.status = "Rusak"
                from app.models.inventory import UnitConditionHistory
                self.db.add(UnitConditionHistory(unit_id=u.id, old_status=old, new_status="Rusak", reason="Tiket Berat/Kritis dibuka", changed_by=self.user_id))
        await self._audit("ticket", t.id, "triage", reason=note)
        await self.db.commit()
        await self.db.refresh(t)
        return t

    async def add_action(self, ticket_id, data: dict):
        t = await self.get_ticket(ticket_id)
        if t.status not in ("Ditriase", "Dalam Perbaikan", "Menunggu Suku Cadang/Vendor"):
            raise ConflictError("Tiket tidak dalam status yang bisa ditindak")
        a = TicketAction(ticket_id=t.id, **data)
        self.db.add(a)
        if data.get("type") == "vendor":
            t.status = "Menunggu Suku Cadang/Vendor"
        else:
            t.status = "Dalam Perbaikan"
        await self.db.commit()
        await self.db.refresh(a)
        return a

    async def verify(self, ticket_id, result, test_notes):
        t = await self.get_ticket(ticket_id)
        if result == "pass":
            t.status = "Terverifikasi"
            t.verified_at = datetime.now(timezone.utc)
            if t.unit_id:
                from app.models.inventory import Unit
                u = (await self.db.execute(select(Unit).where(Unit.id == t.unit_id))).scalar_one_or_none()
                if u:
                    old = u.status
                    u.status = "Siap Pakai"
                    u.verified_at = datetime.now(timezone.utc)
                    from app.models.inventory import UnitConditionHistory
                    self.db.add(UnitConditionHistory(unit_id=u.id, old_status=old, new_status="Siap Pakai", reason="Verifikasi tiket lulus", changed_by=self.user_id))
        else:
            t.status = "Tidak Dapat Diperbaiki"
            t.closed_reason = test_notes
            if t.unit_id:
                from app.models.inventory import Unit
                u = (await self.db.execute(select(Unit).where(Unit.id == t.unit_id))).scalar_one_or_none()
                if u:
                    old = u.status
                    u.status = "Dinonaktifkan"
                    from app.models.inventory import UnitConditionHistory
                    self.db.add(UnitConditionHistory(unit_id=u.id, old_status=old, new_status="Dinonaktifkan", reason="Tiket tidak dapat diperbaiki", changed_by=self.user_id))
        await self._audit("ticket", t.id, "verify", after={"result": result}, reason=test_notes)
        await self.db.commit()
        await self.db.refresh(t)
        return t

    async def list_vendors(self):
        r = await self.db.execute(select(Vendor).order_by(Vendor.name))
        return list(r.scalars().all())
    async def create_vendor(self, data: dict):
        v = Vendor(**data)
        self.db.add(v)
        await self.db.commit()
        await self.db.refresh(v)
        return v

    async def update_vendor(self, vendor_id, data: dict):
        from uuid import UUID
        v = (await self.db.execute(select(Vendor).where(Vendor.id == vendor_id))).scalar_one_or_none()
        if not v:
            raise NotFoundError("Vendor tidak ditemukan")
        for k, val in data.items():
            if hasattr(v, k) and val is not None:
                setattr(v, k, val)
        await self.db.commit()
        await self.db.refresh(v)
        return v

    async def delete_vendor(self, vendor_id):
        from uuid import UUID
        v = (await self.db.execute(select(Vendor).where(Vendor.id == vendor_id))).scalar_one_or_none()
        if not v:
            raise NotFoundError("Vendor tidak ditemukan")
        await self.db.delete(v)
        await self.db.commit()
        return {"deleted": True}
