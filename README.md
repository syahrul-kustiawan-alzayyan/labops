# LabOps ITG — Aplikasi Operasional Laboratorium Ilmu Komputer

Stack: FastAPI (Python) + React (Vite) + PostgreSQL, dijalankan via Docker Compose.

## Quick Start (dev)

1. Salin env: `cp .env.example .env` (Windows: `copy .env.example .env`).
2. Jalankan: `docker compose up -d --build`.
3. Migrasi DB: `docker compose exec backend alembic upgrade head`.
4. Seed admin: `docker compose exec backend python -m scripts.seed`.
5. Buka: frontend `http://localhost:5173`, API docs `http://localhost:8000/docs`.

## Struktur
- `backend/` — FastAPI app
- `frontend/` — React SPA
- `workflow/` — PRD, HLD, LLD, template data, review report
- `storage/` — file storage (volume)

## Dokumen
- PRD: `workflow/prd.md` (v1.2, 准出)
- HLD: `workflow/hld.md`
- LLD: `workflow/lld.md`
- Template data awal: `workflow/templates/`

## Catatan
Hosting belum tersedia (Q1 terbuka). Untuk dev, jalankan lokal via Docker. Untuk prod, provision VPS sesuai HLD 9.4.