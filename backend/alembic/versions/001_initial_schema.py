"""Initial schema for LabOps ITG.

Revision ID: 001_initial
Revises: 
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # users
    op.create_table("users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), server_default="admin"),
        sa.Column("failed_attempts", sa.Integer, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # labs
    op.create_table("labs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_name", sa.String(50), unique=True, nullable=False),
        sa.Column("aliases", postgresql.JSONB, nullable=True),
        sa.Column("capacity", sa.Integer, server_default="30"),
        sa.Column("facilities", postgresql.JSONB, nullable=True),
        sa.Column("capabilities", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), server_default="aktif"),
    )
    # components
    op.create_table("components",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("is_consumable", sa.Boolean, server_default="false"),
        sa.Column("min_stock", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # units
    op.create_table("units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("component_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("components.id"), nullable=False),
        sa.Column("serial_no", sa.String(100), nullable=True),
        sa.Column("brand_model", sa.String(200), nullable=True),
        sa.Column("lab_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("labs.id"), nullable=False),
        sa.Column("placement", sa.String(200), nullable=True),
        sa.Column("acquired_at", sa.Date, nullable=True),
        sa.Column("warranty_until", sa.Date, nullable=True),
        sa.Column("funding_source", sa.String(100), nullable=True),
        sa.Column("ownership", sa.String(100), nullable=True),
        sa.Column("status", sa.String(30), server_default="Siap Pakai"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_units_code", "units", ["code"])
    # unit_condition_history
    op.create_table("unit_condition_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id"), nullable=False),
        sa.Column("old_status", sa.String(30), nullable=False),
        sa.Column("new_status", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    # unit_verifications
    op.create_table("unit_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id"), nullable=False),
        sa.Column("result", sa.String(10), nullable=False),
        sa.Column("failed_items", postgresql.JSONB, nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    # checklists
    op.create_table("checklists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lab_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("labs.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("items", postgresql.JSONB, nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("conclusion", sa.String(20), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    # consumables
    op.create_table("consumables",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("component_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("components.id"), nullable=False),
        sa.Column("lab_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("labs.id"), nullable=False),
        sa.Column("stock", sa.Integer, server_default="0"),
        sa.Column("min_stock", sa.Integer, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # vendors
    op.create_table("vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("service_type", sa.String(200), nullable=True),
        sa.Column("contact", sa.String(200), nullable=True),
        sa.Column("performance_notes", sa.Text, nullable=True),
    )
    # tickets
    op.create_table("tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("number", sa.String(30), unique=True, nullable=False),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id"), nullable=True),
        sa.Column("reporter", sa.String(200), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("impact", sa.Boolean, server_default="false"),
        sa.Column("priority", sa.String(10), nullable=False),
        sa.Column("status", sa.String(30), server_default="Dilaporkan"),
        sa.Column("kronologi", sa.Text, nullable=True),
        sa.Column("due_response_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_remediation_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("triaged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("closed_reason", sa.Text, nullable=True),
    )
    # ticket_actions
    op.create_table("ticket_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("diagnosis", sa.Text, nullable=True),
        sa.Column("action", sa.Text, nullable=True),
        sa.Column("sparepart", sa.Text, nullable=True),
        sa.Column("cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # semesters
    op.create_table("semesters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("operating_start", sa.Time, server_default="07:30:00"),
        sa.Column("operating_end", sa.Time, server_default="18:30:00"),
        sa.Column("slot_presets", postgresql.JSONB, nullable=True),
    )
    # lecturers
    op.create_table("lecturers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("canonical_name", sa.String(200), nullable=False),
        sa.Column("aliases", postgresql.JSONB, nullable=True),
        sa.Column("nidn", sa.String(30), nullable=True),
        sa.Column("role", sa.String(30), server_default="dosen"),
    )
    # courses
    op.create_table("courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("prodi", sa.String(50), nullable=False),
        sa.Column("sks", sa.Integer, server_default="2"),
    )
    # classes
    op.create_table("classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("prodi", sa.String(50), nullable=False),
        sa.Column("semester", sa.String(50), nullable=False),
        sa.Column("academic_year", sa.String(20), nullable=False),
    )
    # sessions
    op.create_table("sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String(30), server_default="praktikum"),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classes.id"), nullable=True),
        sa.Column("lab_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("labs.id"), nullable=False),
        sa.Column("day_of_week", sa.Integer, nullable=False),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=False),
        sa.Column("week_start", sa.Integer, server_default="1"),
        sa.Column("week_end", sa.Integer, server_default="16"),
        sa.Column("student_count", sa.Integer, server_default="0"),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schedule_versions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # session_lecturers
    op.create_table("session_lecturers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("lecturer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lecturers.id"), nullable=False),
        sa.Column("role", sa.String(20), server_default="dosen"),
    )
    # session_changes
    op.create_table("session_changes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("before_data", postgresql.JSONB, nullable=True),
        sa.Column("after_data", postgresql.JSONB, nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    # schedule_versions
    op.create_table("schedule_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("semester_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("semesters.id"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", sa.String(20), server_default="published"),
        sa.Column("published_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("previous_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schedule_versions.id"), nullable=True),
    )
    # social_accounts
    op.create_table("social_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("prodi", sa.String(50), nullable=True),
        sa.Column("tone", sa.String(100), nullable=True),
        sa.Column("audience", sa.String(200), nullable=True),
        sa.Column("ideal_posting_time", sa.Time, nullable=True),
    )
    # content_ideas
    op.create_table("content_ideas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("target_date", sa.Date, nullable=True),
        sa.Column("target_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("social_accounts.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # contents
    op.create_table("contents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("social_accounts.id"), nullable=False),
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_ideas.id"), nullable=True),
        sa.Column("caption", sa.Text, nullable=True),
        sa.Column("scheduled_date", sa.Date, nullable=True),
        sa.Column("scheduled_time", sa.Time, nullable=True),
        sa.Column("status", sa.String(20), server_default="Ide"),
        sa.Column("revision_no", sa.Integer, server_default="1"),
        sa.Column("parent_content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id"), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # content_checklists
    op.create_table("content_checklists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id"), unique=True, nullable=False),
        sa.Column("items", postgresql.JSONB, nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    # content_assets
    op.create_table("content_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # reminders
    op.create_table("reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("send_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    # activity_logs
    op.create_table("activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("before_data", postgresql.JSONB, nullable=True),
        sa.Column("after_data", postgresql.JSONB, nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("is_break_glass", sa.Boolean, server_default="false"),
    )
    # notifications
    op.create_table("notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # settings
    op.create_table("settings",
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("value", postgresql.JSONB, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    # import_batches
    op.create_table("import_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("total_rows", sa.Integer, server_default="0"),
        sa.Column("success", sa.Integer, server_default="0"),
        sa.Column("failed", sa.Integer, server_default="0"),
        sa.Column("duplicate", sa.Integer, server_default="0"),
        sa.Column("status", sa.String(20), server_default="active"),
    )
    # reports
    op.create_table("reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scope", postgresql.JSONB, nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("file_path", sa.String(500), nullable=True),
    )

def downgrade():
    for t in ["reports", "import_batches", "settings", "notifications", "activity_logs",
              "reminders", "content_assets", "content_checklists", "contents", "content_ideas",
              "social_accounts", "schedule_versions", "session_changes", "session_lecturers",
              "sessions", "classes", "courses", "lecturers", "semesters", "ticket_actions",
              "tickets", "vendors", "consumables", "checklists", "unit_verifications",
              "unit_condition_history", "units", "components", "labs", "users"]:
        op.drop_table(t)