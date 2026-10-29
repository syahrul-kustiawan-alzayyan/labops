import uuid
from datetime import datetime, timezone, timedelta, date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.social import SocialAccount, ContentIdea, Content, ContentChecklist, ContentAsset, Reminder
from app.models.core import ActivityLog
from app.core.errors import NotFoundError, ConflictError

VALID_TRANSITIONS = {
    "Ide": ["Draf", "Dibatalkan"],
    "Draf": ["Disetujui", "Dibatalkan"],
    "Disetujui": ["Terjadwal", "Draf", "Dibatalkan"],
    "Terjadwal": ["Terposting", "Ditunda", "Dibatalkan"],
    "Ditunda": ["Terjadwal", "Dibatalkan"],
    "Terposting": [],
    "Dibatalkan": [],
}

class SocialService:
    def __init__(self, db: AsyncSession, user_id=None):
        self.db = db
        self.user_id = user_id

    async def _audit(self, entity_type, entity_id, action, before=None, after=None, reason=None):
        self.db.add(ActivityLog(actor_id=self.user_id, entity_type=entity_type, entity_id=entity_id,
                                action=action, before_data=before, after_data=after, reason=reason))

    async def list_accounts(self):
        r = await self.db.execute(select(SocialAccount).order_by(SocialAccount.name))
        return list(r.scalars().all())

    async def create_account(self, data: dict):
        a = SocialAccount(**data)
        self.db.add(a)
        await self.db.commit()
        await self.db.refresh(a)
        return a

    async def create_idea(self, data: dict):
        i = ContentIdea(**data)
        self.db.add(i)
        await self.db.commit()
        await self.db.refresh(i)
        return i

    async def create_content(self, data: dict):
        c = Content(**data)
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        # checklist kosong
        cl = ContentChecklist(content_id=c.id, items=[])
        self.db.add(cl)
        await self.db.commit()
        return c

    async def get_content(self, content_id):
        r = await self.db.execute(select(Content).where(Content.id == content_id))
        c = r.scalar_one_or_none()
        if not c:
            raise NotFoundError("Konten tidak ditemukan")
        return c

    async def list_contents(self, account_id=None, status=None):
        q = select(Content)
        if account_id:
            q = q.where(Content.account_id == account_id)
        if status:
            q = q.where(Content.status == status)
        q = q.order_by(Content.created_at.desc())
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def update_content(self, content_id, data: dict):
        c = await self.get_content(content_id)
        for k, v in data.items():
            if hasattr(c, k) and v is not None:
                setattr(c, k, v)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def get_checklist(self, content_id):
        r = await self.db.execute(select(ContentChecklist).where(ContentChecklist.content_id == content_id))
        cl = r.scalar_one_or_none()
        if not cl:
            raise NotFoundError("Checklist tidak ditemukan")
        return cl

    async def update_checklist(self, content_id, items: list):
        cl = await self.get_checklist(content_id)
        cl.items = items
        if all(i.get("checked") for i in items) and items:
            cl.completed_at = datetime.now(timezone.utc)
        else:
            cl.completed_at = None
        await self.db.commit()
        await self.db.refresh(cl)
        return cl

    async def approve(self, content_id, user_id):
        c = await self.get_content(content_id)
        cl = await self.get_checklist(content_id)
        if not cl.items or not all(i.get("checked") for i in cl.items):
            raise ConflictError("Checklist belum 100%")
        if c.status not in ("Draf",):
            raise ConflictError(f"Status {c.status} tidak dapat disetujui")
        c.status = "Disetujui"
        cl.approved_by = user_id
        cl.approved_at = datetime.now(timezone.utc)
        await self._audit("content", c.id, "approve", after={"status": "Disetujui"})
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def schedule(self, content_id, sched_date, sched_time):
        c = await self.get_content(content_id)
        if c.status != "Disetujui":
            raise ConflictError("Konten belum disetujui")
        c.scheduled_date = sched_date
        c.scheduled_time = sched_time
        c.status = "Terjadwal"
        # jadwalkan pengingat H-3/H-1/H-0 (H-3 hanya untuk Terjadwal)
        from datetime import timedelta
        base = datetime.combine(sched_date, sched_time).replace(tzinfo=timezone.utc) if False else None
        # simpan reminder records (send_at dalam WIB -> UTC)
        for kind, delta in [("H-3", timedelta(days=3)), ("H-1", timedelta(days=1)), ("H-0", timedelta(hours=2))]:
            send_at = datetime.combine(sched_date, sched_time or datetime.now(timezone.utc).time()).replace(tzinfo=timezone.utc) - delta
            # H-0: 2 jam sebelum jam posting
            if kind == "H-0":
                send_at = datetime.combine(sched_date, sched_time).replace(tzinfo=timezone.utc) - timedelta(hours=2)
            self.db.add(Reminder(entity_type="content", entity_id=c.id, kind=kind, send_at=send_at))
        await self._audit("content", c.id, "schedule", after={"status": "Terjadwal", "date": str(sched_date)})
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def mark_posted(self, content_id, posted_at=None):
        c = await self.get_content(content_id)
        if c.status != "Terjadwal":
            raise ConflictError("Konten belum terjadwal")
        c.status = "Terposting"
        c.posted_at = posted_at or datetime.now(timezone.utc)
        # kunci aset (set version final)
        await self._audit("content", c.id, "mark_posted", after={"status": "Terposting"})
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def reopen(self, content_id):
        c = await self.get_content(content_id)
        if c.status != "Terposting":
            raise ConflictError("Hanya konten Terposting yang dapat dibuka kembali")
        # BR-27: buat revisi baru, versi lama tetap final
        new = Content(
            title=c.title, account_id=c.account_id, idea_id=c.idea_id,
            caption=c.caption, status="Draf", revision_no=c.revision_no + 1,
            parent_content_id=c.id,
        )
        self.db.add(new)
        await self.db.commit()
        await self.db.refresh(new)
        cl = ContentChecklist(content_id=new.id, items=[])
        self.db.add(cl)
        await self.db.commit()
        await self._audit("content", new.id, "reopen", after={"revision": new.revision_no, "parent": str(c.id)})
        await self.db.commit()
        return new

    async def reschedule(self, content_id, sched_date, sched_time, reason):
        c = await self.get_content(content_id)
        if c.status not in ("Terjadwal", "Ditunda"):
            raise ConflictError("Status tidak dapat dijadwalkan ulang")
        c.scheduled_date = sched_date
        c.scheduled_time = sched_time
        c.status = "Terjadwal"
        await self._audit("content", c.id, "reschedule", reason=reason)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def cancel_content(self, content_id, reason):
        c = await self.get_content(content_id)
        if c.status in ("Terposting", "Dibatalkan"):
            raise ConflictError("Status final, tidak dapat dibatalkan")
        c.status = "Dibatalkan"
        await self._audit("content", c.id, "cancel", reason=reason)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def get_calendar(self, month: int, year: int, account_id=None):
        from sqlalchemy import extract
        q = select(Content).where(
            extract("month", Content.scheduled_date) == month,
            extract("year", Content.scheduled_date) == year,
        )
        if account_id:
            q = q.where(Content.account_id == account_id)
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def get_due_list(self):
        today = datetime.now(timezone.utc).date()
        r = await self.db.execute(select(Content).where(Content.status == "Terjadwal", Content.scheduled_date <= today))
        return list(r.scalars().all())

    async def migrate_legacy(self, rows: list):
        # deterministik (PRD 6.7.2)
        created = []
        for row in rows:
            title = row.get("Konten/Kegiatan") or row.get("title")
            raw_date = row.get("Tanggal") or row.get("date")
            status_lama = row.get("Status")
            keterangan = row.get("Keterangan")
            sched_date = None
            # parse date dd/mm/yyyy
            if raw_date:
                try:
                    d, m, y = raw_date.split("/")
                    sched_date = date(int(y), int(m), int(d))
                except Exception:
                    sched_date = None
            if not sched_date:
                status_baru = "Ide"
            elif status_lama == "Terupload" or keterangan == "Terupload":
                status_baru = "Terposting"
            elif status_lama == "Di Jadwalkan":
                status_baru = "Draf"  # naik ke Terjadwal hanya setelah checklist 100% + akun
            elif status_lama == "Di Terima":
                status_baru = "Draf"
            else:
                status_baru = "Draf"
            # default akun = Fakultas (flag perlu re-tag)
            acc = (await self.db.execute(select(SocialAccount).where(SocialAccount.type == "fakultas"))).scalar_one_or_none()
            c = Content(title=title, account_id=acc.id if acc else None, caption=None,
                        scheduled_date=sched_date, status=status_baru)
            self.db.add(c)
            created.append(c)
        await self.db.commit()
        for c in created:
            await self.db.refresh(c)
        return created