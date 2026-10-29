import uuid
from datetime import datetime, timezone, timedelta, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import Component, Unit, UnitConditionHistory, UnitVerification, Checklist, Consumable, Lab
from app.models.core import ActivityLog
from app.core.errors import NotFoundError, ConflictError

class InventoryService:
    def __init__(self, db: AsyncSession, user_id: uuid.UUID | None = None):
        self.db = db
        self.user_id = user_id

    async def _audit(self, entity_type, entity_id, action, before=None, after=None, reason=None):
        self.db.add(ActivityLog(actor_id=self.user_id, entity_type=entity_type, entity_id=entity_id,
                                action=action, before_data=before, after_data=after, reason=reason))

    # Components
    async def list_components(self):
        r = await self.db.execute(select(Component).order_by(Component.name))
        return list(r.scalars().all())

    async def create_component(self, data: dict):
        c = Component(**data)
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    # Units
    async def list_units(self, lab_id=None, status=None, search=None):
        q = select(Unit)
        if lab_id:
            q = q.where(Unit.lab_id == lab_id)
        if status:
            q = q.where(Unit.status == status)
        if search:
            q = q.where(Unit.code.ilike(f"%{search}%"))
        q = q.order_by(Unit.code)
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def get_unit(self, unit_id):
        r = await self.db.execute(select(Unit).where(Unit.id == unit_id))
        u = r.scalar_one_or_none()
        if not u:
            raise NotFoundError("Unit tidak ditemukan")
        return u

    async def create_unit(self, data: dict):
        exists = (await self.db.execute(select(Unit).where(Unit.code == data["code"]))).scalar_one_or_none()
        if exists:
            raise ConflictError("Kode unit sudah ada")
        u = Unit(**data)
        self.db.add(u)
        await self.db.commit()
        await self.db.refresh(u)
        await self._audit("unit", u.id, "create", after={"code": u.code, "status": u.status})
        await self.db.commit()
        return u

    async def update_unit_status(self, unit_id, new_status, reason):
        u = await self.get_unit(unit_id)
        old = u.status
        # BR-26: Dalam Perbaikan hanya sah bila ada tiket aktif (cek di router/repair service); di sini hanya validasi transisi dasar
        u.status = new_status
        self.db.add(UnitConditionHistory(unit_id=u.id, old_status=old, new_status=new_status, reason=reason, changed_by=self.user_id))
        await self._audit("unit", u.id, "status_change", before={"status": old}, after={"status": new_status}, reason=reason)
        await self.db.commit()
        await self.db.refresh(u)
        return u

    async def archive_unit(self, unit_id, reason):
        u = await self.get_unit(unit_id)
        u.archived_at = datetime.now(timezone.utc)
        u.archived_reason = reason
        await self._audit("unit", u.id, "archive", reason=reason)
        await self.db.commit()
        await self.db.refresh(u)
        return u

    # Checklists
    async def create_checklist(self, lab_id, date_val, items):
        # satu checklist per lab+tanggal
        existing = (await self.db.execute(select(Checklist).where(Checklist.lab_id == lab_id, Checklist.date == date_val))).scalar_one_or_none()
        if existing:
            raise ConflictError("Checklist untuk lab+tanggal ini sudah ada")
        score = (sum(1 for i in items if i.get("result") == "pass") / len(items) * 100) if items else 0
        # kesiapan biner BR-02: >=90% workstation + 100% item kritis + 0 tiket Kritis + confirmed
        required_items = [i for i in items if i.get("required")]
        critical_ok = all(i.get("result") == "pass" for i in required_items)
        conclusion = "siap" if (score >= 90 and critical_ok) else "tidak_siap"
        c = Checklist(lab_id=lab_id, date=date_val, items=items, score=round(score, 2), conclusion=conclusion)
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def list_checklists(self, lab_id=None):
        q = select(Checklist)
        if lab_id:
            q = q.where(Checklist.lab_id == lab_id)
        q = q.order_by(Checklist.date.desc())
        r = await self.db.execute(q)
        return list(r.scalars().all())

    # Verification
    async def verify_unit(self, unit_id, result, failed_items=None):
        u = await self.get_unit(unit_id)
        v = UnitVerification(unit_id=u.id, result=result, failed_items=failed_items,
                             valid_until=datetime.now(timezone.utc) + timedelta(days=90),
                             verified_by=self.user_id)
        self.db.add(v)
        u.verified_at = datetime.now(timezone.utc)
        await self._audit("unit", u.id, "verify", after={"result": result})
        await self.db.commit()
        await self.db.refresh(v)
        return v

    # Unit history
    async def get_unit_history(self, unit_id):
        u = await self.get_unit(unit_id)
        r = await self.db.execute(select(UnitConditionHistory).where(UnitConditionHistory.unit_id == unit_id).order_by(UnitConditionHistory.changed_at.desc()))
        return list(r.scalars().all())

    async def get_unit_tickets(self, unit_id):
        from app.models.repairs import Ticket
        r = await self.db.execute(select(Ticket).where(Ticket.unit_id == unit_id).order_by(Ticket.created_at.desc()))
        return list(r.scalars().all())

    # Import
    async def import_units(self, rows: list, mode: str = "preview"):
        valid = []
        errors = []
        duplicates = 0
        for idx, row in enumerate(rows, start=2):  # row 1 = header
            try:
                code = (row.get("code") or "").strip().upper()
                if not code:
                    errors.append({"row": idx, "field": "code", "message": "Kode unit wajib"})
                    continue
                # duplicate check
                exists = (await self.db.execute(select(Unit).where(Unit.code == code))).scalar_one_or_none()
                if exists:
                    duplicates += 1
                    errors.append({"row": idx, "field": "code", "message": f"Kode {code} sudah ada (duplikat)"})
                    continue
                # validate lab
                lab_name = (row.get("lab") or "").strip()
                lab = (await self.db.execute(select(Lab).where(Lab.canonical_name == lab_name))).scalar_one_or_none()
                if not lab:
                    errors.append({"row": idx, "field": "lab", "message": f"Lab '{lab_name}' tidak ditemukan"})
                    continue
                # validate component
                comp_name = (row.get("component") or "").strip()
                comp = (await self.db.execute(select(Component).where(Component.name == comp_name))).scalar_one_or_none()
                if not comp:
                    errors.append({"row": idx, "field": "component", "message": f"Komponen '{comp_name}' tidak ditemukan"})
                    continue
                status = (row.get("condition") or "Siap Pakai").strip()
                if status not in ("Siap Pakai", "Perlu Perhatian", "Rusak", "Dalam Perbaikan", "Dinonaktifkan", "Hilang"):
                    errors.append({"row": idx, "field": "condition", "message": f"Status '{status}' tidak valid"})
                    continue
                # parse dates
                from datetime import datetime as dt
                def parse_date(s):
                    s = (s or "").strip()
                    if not s:
                        return None
                    try:
                        d, m, y = s.split("/")
                        return dt(int(y), int(m), int(d)).date()
                    except Exception:
                        return None
                acquired = parse_date(row.get("acquired_at"))
                warranty = parse_date(row.get("warranty_until"))
                valid.append({
                    "code": code, "component_id": comp.id, "brand_model": row.get("brand_model"),
                    "serial_no": row.get("serial_no"), "lab_id": lab.id,
                    "placement": row.get("placement"), "acquired_at": acquired,
                    "warranty_until": warranty, "funding_source": row.get("funding_source"),
                    "ownership": row.get("ownership"), "status": status,
                })
            except Exception as e:
                errors.append({"row": idx, "field": "general", "message": str(e)})

        if mode == "preview":
            return {"total": len(rows), "valid": len(valid), "invalid": len(errors), "duplicate": duplicates,
                    "errors": errors, "preview": valid[:20]}

        # commit mode
        batch_id = uuid.uuid4()
        from app.models.core import ImportBatch
        batch = ImportBatch(type="inventory", total_rows=len(rows), success=0, failed=len(errors), duplicate=duplicates, status="active", created_by=self.user_id)
        self.db.add(batch)
        await self.db.flush()
        success = 0
        for v in valid:
            u = Unit(**v)
            self.db.add(u)
            success += 1
        batch.success = success
        await self.db.commit()
        return {"batch_id": str(batch.id), "total": len(rows), "success": success, "failed": len(errors), "duplicate": duplicates, "errors": errors}
        r = await self.db.execute(select(Lab).order_by(Lab.canonical_name))
        return list(r.scalars().all())

    async def create_lab(self, data: dict):
        lab = Lab(**data)
        self.db.add(lab)
        await self.db.commit()
        await self.db.refresh(lab)
        return lab

    # Consumables
    async def list_consumables(self):
        r = await self.db.execute(select(Consumable))
        return list(r.scalars().all())

    async def create_consumable(self, data: dict):
        c = Consumable(**data)
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        return c