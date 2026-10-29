import uuid
from datetime import datetime, timezone, time, date, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scheduling import Session, SessionLecturer, SessionChange, ScheduleVersion, Semester, Lecturer, Course, ClassGroup
from app.models.inventory import Lab
from app.core.errors import NotFoundError, ConflictError

class SchedulingService:
    def __init__(self, db: AsyncSession, user_id=None):
        self.db = db
        self.user_id = user_id

    async def _to_minutes(self, t: time) -> int:
        return t.hour * 60 + t.minute

    async def validate_session(self, data: dict, exclude_id=None):
        """Returns (conflicts: list, warnings: list)."""
        conflicts = []
        warnings = []
        lab_id = data["lab_id"]
        day = data["day_of_week"]
        start = data["start_time"]
        end = data["end_time"]
        ws = data["week_start"]
        we = data["week_end"]
        start_m = self._to_minutes(start)
        end_m = self._to_minutes(end)

        # maintenance blocks & existing sessions in same lab/day with week overlap
        q = select(Session).where(Session.lab_id == lab_id, Session.day_of_week == day)
        if exclude_id:
            q = q.where(Session.id != exclude_id)
        r = await self.db.execute(q)
        for s in r.scalars().all():
            if not (we < s.week_start or ws > s.week_end):  # week overlap
                s_start = self._to_minutes(s.start_time)
                s_end = self._to_minutes(s.end_time)
                # half-open interval overlap
                if start_m < s_end and s_start < end_m:
                    if s.type == "maintenance":
                        conflicts.append({"session_id": str(s.id), "reason": "maintenance_overlap", "detail": f"{s.start_time}-{s.end_time}"})
                    else:
                        conflicts.append({"session_id": str(s.id), "reason": "room_conflict", "detail": f"{s.start_time}-{s.end_time}"})
                else:
                    # adjacent check: jeda < 10 menit
                    gap = abs(s_start - end_m) if s_start >= end_m else abs(start_m - s_end)
                    if 0 < gap < 10:
                        warnings.append({"session_id": str(s.id), "reason": "adjacent_under_10", "gap": gap})

        # lecturer conflict
        for lid in data.get("lecturer_ids", []):
            q2 = select(Session).join(SessionLecturer, SessionLecturer.session_id == Session.id).where(
                SessionLecturer.lecturer_id == lid, Session.day_of_week == day)
            if exclude_id:
                q2 = q2.where(Session.id != exclude_id)
            r2 = await self.db.execute(q2)
            for s in r2.scalars().all():
                if not (we < s.week_start or ws > s.week_end):
                    s_start = self._to_minutes(s.start_time)
                    s_end = self._to_minutes(s.end_time)
                    if start_m < s_end and s_start < end_m:
                        conflicts.append({"session_id": str(s.id), "reason": "lecturer_conflict"})

        # class conflict
        if data.get("class_id"):
            q3 = select(Session).where(Session.class_id == data["class_id"], Session.day_of_week == day)
            if exclude_id:
                q3 = q3.where(Session.id != exclude_id)
            r3 = await self.db.execute(q3)
            for s in r3.scalars().all():
                if not (we < s.week_start or ws > s.week_end):
                    s_start = self._to_minutes(s.start_time)
                    s_end = self._to_minutes(s.end_time)
                    if start_m < s_end and s_start < end_m:
                        conflicts.append({"session_id": str(s.id), "reason": "class_conflict"})

        return conflicts, warnings

    async def create_session(self, data: dict):
        conflicts, warnings = await self.validate_session(data)
        if conflicts:
            raise ConflictError("Bentrok jadwal", details={"conflicts": conflicts, "warnings": warnings})
        # kapasitas check (BR-23): student_count vs available workstations
        lab = (await self.db.execute(select(Lab).where(Lab.id == data["lab_id"]))).scalar_one_or_none()
        if lab and data.get("student_count", 0) > lab.capacity:
            if not data.get("override_reason"):
                raise ConflictError("Jumlah mahasiswa melebihi kapasitas ruang", details={"capacity": lab.capacity})
        s = Session(
            type=data.get("type", "praktikum"),
            course_id=data.get("course_id"),
            class_id=data.get("class_id"),
            lab_id=data["lab_id"],
            day_of_week=data["day_of_week"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            week_start=data.get("week_start", 1),
            week_end=data.get("week_end", 16),
            student_count=data.get("student_count", 0),
            status="draft",
        )
        self.db.add(s)
        await self.db.flush()
        for lid in data.get("lecturer_ids", []):
            self.db.add(SessionLecturer(session_id=s.id, lecturer_id=lid, role=data.get("lecturer_role", "dosen")))
        await self.db.commit()
        await self.db.refresh(s)
        return s, warnings

    async def list_sessions(self, lab_id=None, prodi=None, lecturer_id=None):
        from app.models.scheduling import SessionLecturer
        q = select(Session)
        if lab_id:
            q = q.where(Session.lab_id == lab_id)
        if lecturer_id:
            sub = select(SessionLecturer.session_id).where(SessionLecturer.lecturer_id == lecturer_id)
            q = q.where(Session.id.in_(sub))
        if prodi:
            # filter via class -> course -> prodi
            from app.models.scheduling import ClassGroup, Course
            sub2 = select(ClassGroup.id).join(Course, ClassGroup.course_id == Course.id).where(Course.prodi == prodi)
            q = q.where(Session.class_id.in_(sub2))
        q = q.order_by(Session.day_of_week, Session.start_time)
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def publish_version(self, semester_id, user_id):
        # cek 0 konflik: validasi semua sesi draft
        sessions = (await self.db.execute(select(Session).where(Session.status == "draft"))).scalars().all()
        for s in sessions:
            data = {
                "lab_id": s.lab_id, "day_of_week": s.day_of_week,
                "start_time": s.start_time, "end_time": s.end_time,
                "week_start": s.week_start, "week_end": s.week_end,
                "lecturer_ids": [], "class_id": s.class_id,
            }
            conflicts, _ = await self.validate_session(data, exclude_id=s.id)
            if conflicts:
                raise ConflictError("Masih ada bentrok, tidak dapat menerbitkan", details={"conflicts": conflicts})
        v = ScheduleVersion(semester_id=semester_id, published_by=user_id, status="published")
        self.db.add(v)
        await self.db.flush()
        for s in sessions:
            s.status = "published"
            s.version_id = v.id
        await self.db.commit()
        await self.db.refresh(v)
        return v

    async def list_labs(self):
        r = await self.db.execute(select(Lab).order_by(Lab.canonical_name))
        return list(r.scalars().all())

    async def list_lecturers(self):
        r = await self.db.execute(select(Lecturer).order_by(Lecturer.canonical_name))
        return list(r.scalars().all())

    async def list_courses(self):
        r = await self.db.execute(select(Course).order_by(Course.code))
        return list(r.scalars().all())

    async def list_classes(self):
        r = await self.db.execute(select(ClassGroup).order_by(ClassGroup.code))
        return list(r.scalars().all())

    async def list_semesters(self):
        r = await self.db.execute(select(Semester).order_by(Semester.start_date.desc()))
        return list(r.scalars().all())