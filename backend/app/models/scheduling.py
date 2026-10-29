import uuid
from datetime import datetime, timezone, time, date
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Time, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Semester(Base):
    __tablename__ = "semesters"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    operating_start: Mapped[time] = mapped_column(Time, default=time(7, 30))
    operating_end: Mapped[time] = mapped_column(Time, default=time(18, 30))
    slot_presets: Mapped[list | None] = mapped_column(JSON, nullable=True)

class Lecturer(Base):
    __tablename__ = "lecturers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    canonical_name: Mapped[str] = mapped_column(String(200))
    aliases: Mapped[list | None] = mapped_column(JSON, nullable=True)
    nidn: Mapped[str | None] = mapped_column(String(30), nullable=True)
    role: Mapped[str] = mapped_column(String(30), default="dosen")

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    prodi: Mapped[str] = mapped_column(String(50))
    sks: Mapped[int] = mapped_column(Integer, default=2)

class ClassGroup(Base):
    __tablename__ = "classes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"))
    prodi: Mapped[str] = mapped_column(String(50))
    semester: Mapped[str] = mapped_column(String(50))
    academic_year: Mapped[str] = mapped_column(String(20))

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(30), default="praktikum")
    course_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("courses.id"), nullable=True)
    class_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("classes.id"), nullable=True)
    lab_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labs.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0=Sen..5=Sab
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    week_start: Mapped[int] = mapped_column(Integer, default=1)
    week_end: Mapped[int] = mapped_column(Integer, default=16)
    student_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("schedule_versions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class SessionLecturer(Base):
    __tablename__ = "session_lecturers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    lecturer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lecturers.id"))
    role: Mapped[str] = mapped_column(String(20), default="dosen")

class SessionChange(Base):
    __tablename__ = "session_changes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    before_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    changed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

class ScheduleVersion(Base):
    __tablename__ = "schedule_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    semester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("semesters.id"))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(20), default="published")
    published_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    previous_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("schedule_versions.id"), nullable=True)