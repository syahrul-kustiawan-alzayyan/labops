import uuid
from datetime import datetime, timezone, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import Unit, Lab, Checklist
from app.models.repairs import Ticket
from app.models.scheduling import Session
from app.models.social import Content
from app.models.core import ImportBatch

class ReportsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def dashboard(self):
        # kesiapan per lab
        labs = (await self.db.execute(select(Lab).order_by(Lab.canonical_name))).scalars().all()
        kesiapan = []
        for lab in labs:
            units = (await self.db.execute(select(Unit).where(Unit.lab_id == lab.id, Unit.archived_at.is_(None)))).scalars().all()
            total = len(units)
            siap = sum(1 for u in units if u.status == "Siap Pakai")
            pct = (siap / total * 100) if total else 0
            # tiket kritis terbuka
            tk = (await self.db.execute(select(Ticket).where(Ticket.unit_id.in_([u.id for u in units]), Ticket.severity == "Kritis", Ticket.status.notin_(["Terverifikasi", "Duplikat", "Tidak Valid", "Tidak Dapat Diperbaiki"])))).scalars().all()
            # checklist terakhir
            cl = (await self.db.execute(select(Checklist).where(Checklist.lab_id == lab.id).order_by(Checklist.date.desc()))).scalars().first()
            kesiapan.append({
                "lab": lab.canonical_name, "total_unit": total, "siap": siap,
                "persen": round(pct, 1), "tiket_kritis": len(tk),
                "checklist_terakhir": str(cl.date) if cl else None,
                "kesimpulan": cl.conclusion if cl else "belum",
            })
        # tiket terbuka
        tiket_terbuka = (await self.db.execute(select(Ticket).where(Ticket.status.notin_(["Terverifikasi", "Duplikat", "Tidak Valid", "Tidak Dapat Diperbaiki"])))).scalars().all()
        # sesi hari ini
        today_dow = datetime.now(timezone.utc).weekday()  # 0=Mon..6=Sun; PRD 0=Sen..5=Sab
        dow = today_dow if today_dow < 6 else 0
        sesi_hari_ini = (await self.db.execute(select(Session).where(Session.day_of_week == dow))).scalars().all()
        # konten jatuh tempo
        today = datetime.now(timezone.utc).date()
        konten_due = (await self.db.execute(select(Content).where(Content.status == "Terjadwal", Content.scheduled_date <= today))).scalars().all()
        # tugas lewat tenggat
        tiket_terlambat = [t for t in tiket_terbuka if t.due_remediation_at and t.due_remediation_at < datetime.now(timezone.utc)]
        return {
            "kesiapan_lab": kesiapan,
            "tiket_terbuka": len(tiket_terbuka),
            "tiket_terlambat": len(tiket_terlambat),
            "sesi_hari_ini": [{"id": str(s.id), "lab_id": str(s.lab_id), "start": str(s.start_time), "end": str(s.end_time)} for s in sesi_hari_ini],
            "konten_jatuh_tempo": [{"id": str(c.id), "title": c.title, "date": str(c.scheduled_date)} for c in konten_due],
        }

    async def inventory_report(self):
        units = (await self.db.execute(select(Unit))).scalars().all()
        by_status = {}
        for u in units:
            by_status[u.status] = by_status.get(u.status, 0) + 1
        by_lab = {}
        for u in units:
            by_lab[str(u.lab_id)] = by_lab.get(str(u.lab_id), 0) + 1
        return {"total_unit": len(units), "by_status": by_status, "by_lab": by_lab}

    async def repair_report(self):
        tickets = (await self.db.execute(select(Ticket))).scalars().all()
        by_priority = {}
        by_status = {}
        for t in tickets:
            by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
            by_status[t.status] = by_status.get(t.status, 0) + 1
        return {"total": len(tickets), "by_priority": by_priority, "by_status": by_status}

    async def usage_report(self):
        sessions = (await self.db.execute(select(Session))).scalars().all()
        by_lab = {}
        total_minutes = 0
        for s in sessions:
            st = s.start_time; en = s.end_time
            mins = (en.hour * 60 + en.minute) - (st.hour * 60 + st.minute)
            if mins < 0:
                mins += 24 * 60
            total_minutes += mins
            by_lab[str(s.lab_id)] = by_lab.get(str(s.lab_id), 0) + mins
        return {"total_sessions": len(sessions), "total_minutes": total_minutes, "by_lab_minutes": by_lab}

    async def monthly_report(self, period_start, period_end):
        inv = await self.inventory_report()
        rep = await self.repair_report()
        usage = await self.usage_report()
        social = await self.social_report()
        return {
            "period": {"start": str(period_start), "end": str(period_end)},
            "inventory": inv, "repairs": rep, "usage": usage, "social": social,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }