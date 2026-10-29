from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import time as dtime
import csv, io, uuid as _uuid

from app.core.deps import get_db, require_admin
from app.core.errors import NotFoundError, ConflictError, ValidationError
from app.services.scheduling_service import SchedulingService
from app.models.inventory import Lab
from app.models.scheduling import Course, ClassGroup, Lecturer, Session as Sess, SessionChange

router = APIRouter(prefix="/scheduling", tags=["scheduling"])

def svc(db, user):
    return SchedulingService(db, user.id)

@router.get("/labs")
async def list_labs(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_labs()

@router.get("/semesters")
async def list_semesters(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_semesters()

@router.get("/lecturers")
async def list_lecturers(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_lecturers()

@router.get("/courses")
async def list_courses(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_courses()

@router.get("/classes")
async def list_classes(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_classes()

@router.get("/sessions")
async def list_sessions(lab_id: UUID | None = None, prodi: str | None = None, lecturer_id: UUID | None = None,
                       db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_sessions(lab_id, prodi, lecturer_id)

@router.post("/sessions/validate")
async def validate_session(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    conflicts, warnings = await svc(db, user).validate_session(data)
    return {"conflicts": conflicts, "warnings": warnings}

@router.post("/sessions")
async def create_session(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    s, warnings = await svc(db, user).create_session(data)
    return {"id": str(s.id), "status": s.status, "warnings": warnings}

@router.post("/sessions/import")
async def import_schedule(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    service = svc(db, user)
    rows = data.get("rows", [])
    results = {"total": len(rows), "success": 0, "failed": 0, "errors": [], "sessions": []}
    day_map = {"Senin": 0, "Sen": 0, "Selasa": 1, "Sel": 1, "Rabu": 2, "Rab": 2, "Kamis": 3, "Kam": 3, "Jumat": 4, "Jum": 4, "Sabtu": 5, "Sab": 5}
    def parse_time(s):
        s = (s or "").strip().replace(".", ":")
        parts = s.split(":")
        return dtime(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    for idx, row in enumerate(rows, start=2):
        try:
            lab_alias = (row.get("lab_alias") or row.get("lab") or "").strip()
            lab = (await db.execute(select(Lab).where(Lab.canonical_name == lab_alias))).scalar_one_or_none()
            if not lab:
                labs = (await db.execute(select(Lab))).scalars().all()
                for l in labs:
                    if l.aliases and lab_alias in (l.aliases or []):
                        lab = l
                        break
            if not lab:
                results["errors"].append({"row": idx, "message": f"Lab '{lab_alias}' tidak ditemukan"})
                results["failed"] += 1
                continue
            day = day_map.get((row.get("day") or "").strip())
            if day is None:
                try:
                    day = int(row.get("day"))
                except (ValueError, TypeError):
                    results["errors"].append({"row": idx, "message": f"Hari '{row.get('day')}' tidak valid"})
                    results["failed"] += 1
                    continue
            start_t = parse_time(row.get("start_time"))
            end_t = parse_time(row.get("end_time"))
            course = None
            cc = (row.get("course_code") or "").strip()
            if cc:
                course = (await db.execute(select(Course).where(Course.code == cc))).scalar_one_or_none()
            classg = None
            clc = (row.get("class_code") or "").strip()
            if clc:
                classg = (await db.execute(select(ClassGroup).where(ClassGroup.code == clc))).scalar_one_or_none()
            lecturer_ids = []
            lec_name = (row.get("lecturer") or "").strip()
            if lec_name:
                lec = (await db.execute(select(Lecturer).where(Lecturer.canonical_name == lec_name))).scalar_one_or_none()
                if lec:
                    lecturer_ids = [str(lec.id)]
            sess_data = {
                "type": row.get("type", "praktikum"),
                "course_id": str(course.id) if course else None,
                "class_id": str(classg.id) if classg else None,
                "lab_id": str(lab.id),
                "day_of_week": day,
                "start_time": start_t,
                "end_time": end_t,
                "week_start": int(row.get("week_start", 1) or 1),
                "week_end": int(row.get("week_end", 16) or 16),
                "student_count": int(row.get("student_count", 0) or 0),
                "lecturer_ids": lecturer_ids,
                "override_reason": "data historis",
            }
            try:
                s, warnings = await service.create_session(sess_data)
                results["success"] += 1
                results["sessions"].append(str(s.id))
            except Exception as e:
                results["errors"].append({"row": idx, "message": str(e)})
                results["failed"] += 1
        except Exception as e:
            results["errors"].append({"row": idx, "message": str(e)})
            results["failed"] += 1
    return results

@router.put("/sessions/{session_id}")
async def update_session(session_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    s = (await db.execute(select(Sess).where(Sess.id == session_id))).scalar_one_or_none()
    if not s:
        raise NotFoundError("Sesi tidak ditemukan")
    before = {"lab_id": str(s.lab_id), "day": s.day_of_week, "start": str(s.start_time), "end": str(s.end_time),
              "week_start": s.week_start, "week_end": s.week_end, "student_count": s.student_count}
    if "lab_id" in data: s.lab_id = data["lab_id"]
    if "day_of_week" in data: s.day_of_week = int(data["day_of_week"])
    if "start_time" in data:
        parts = data["start_time"].replace(".", ":").split(":")
        s.start_time = dtime(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    if "end_time" in data:
        parts = data["end_time"].replace(".", ":").split(":")
        s.end_time = dtime(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    if "week_start" in data: s.week_start = int(data["week_start"])
    if "week_end" in data: s.week_end = int(data["week_end"])
    if "student_count" in data: s.student_count = int(data["student_count"])
    if "course_id" in data: s.course_id = data["course_id"]
    if "class_id" in data: s.class_id = data["class_id"]
    vdata = {"lab_id": s.lab_id, "day_of_week": s.day_of_week, "start_time": s.start_time, "end_time": s.end_time,
             "week_start": s.week_start, "week_end": s.week_end, "lecturer_ids": [], "class_id": s.class_id,
             "student_count": s.student_count}
    conflicts, warnings = await svc(db, user).validate_session(vdata, exclude_id=s.id)
    if conflicts:
        raise ConflictError("Bentrok jadwal", details={"conflicts": conflicts})
    db.add(SessionChange(session_id=s.id, before_data=before, after_data=vdata, reason=data.get("reason"), changed_by=user.id))
    s.status = "draft"
    await db.commit()
    await db.refresh(s)
    return {"id": str(s.id), "status": s.status, "warnings": warnings}

@router.post("/sessions/{session_id}/cancel")
async def cancel_session(session_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    s = (await db.execute(select(Sess).where(Sess.id == session_id))).scalar_one_or_none()
    if not s:
        raise NotFoundError("Sesi tidak ditemukan")
    if not data.get("reason"):
        raise ValidationError("Alasan pembatalan wajib")
    db.add(SessionChange(session_id=s.id, before_data={"status": s.status}, after_data={"status": "cancelled"}, reason=data["reason"], changed_by=user.id))
    s.status = "cancelled"
    await db.commit()
    await db.refresh(s)
    return {"id": str(s.id), "status": s.status}

@router.post("/versions/publish")
async def publish(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    v = await svc(db, user).publish_version(_uuid.UUID(data["semester_id"]), user.id)
    return {"id": str(v.id), "status": v.status, "published_at": str(v.published_at)}

@router.get("/calendar")
async def calendar(lab_id: UUID | None = None, prodi: str | None = None, lecturer_id: UUID | None = None,
                  db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    sessions = await svc(db, user).list_sessions(lab_id, prodi, lecturer_id)
    return {"sessions": [{"id": str(s.id), "lab_id": str(s.lab_id), "day": s.day_of_week,
                         "start": str(s.start_time), "end": str(s.end_time),
                         "week_start": s.week_start, "week_end": s.week_end, "status": s.status,
                         "course_id": str(s.course_id) if s.course_id else None,
                         "class_id": str(s.class_id) if s.class_id else None} for s in sessions]}

@router.get("/export/schedule")
async def export_schedule_csv(lab_id: UUID | None = None, prodi: str | None = None,
                             db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    service = svc(db, user)
    sessions = await service.list_sessions(lab_id, prodi, None)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Hari", "Jam Mulai", "Jam Selesai", "Minggu", "Ruang", "MK", "Kelas", "Mahasiswa", "Status"])
    day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    for s in sessions:
        w.writerow([day_names[s.day_of_week], str(s.start_time), str(s.end_time), f"{s.week_start}-{s.week_end}",
                    str(s.lab_id), str(s.course_id or ""), str(s.class_id or ""), s.student_count, s.status])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                            headers={"Content-Disposition": "attachment; filename=jadwal_lab.csv"})

@router.get("/export/schedule/pdf")
async def export_schedule_pdf(lab_id: UUID | None = None, prodi: str | None = None,
                             db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    from app.exporters.schedule_pdf import generate_schedule_pdf
    service = svc(db, user)
    sessions = await service.list_sessions(lab_id, prodi, None)
    labs = await service.list_labs()
    courses = await service.list_courses()
    classes = await service.list_classes()
    pdf_bytes = generate_schedule_pdf(sessions, labs, courses, classes,
                                     title="Jadwal Penggunaan Laboratorium",
                                     subtitle=f"Filter: lab={lab_id or 'semua'}, prodi={prodi or 'semua'}")
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=jadwal_lab.pdf"})