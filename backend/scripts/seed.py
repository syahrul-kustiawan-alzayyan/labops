"""Seed master data awal (M0) dari template CSV di workflow/templates."""
import asyncio
import csv
import os
from pathlib import Path

from app.core.database import SessionLocal
from app.models.user import User
from app.models.inventory import Lab, Component
from app.core.security import hash_password

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "workflow" / "templates"

async def seed_admin():
    async with SessionLocal() as db:
        from sqlalchemy import select
        exists = (await db.execute(select(User).where(User.email == "admin@labops.itg"))).scalar_one_or_none()
        if exists:
            print("Admin sudah ada, skip.")
            return
        db.add(User(email="admin@labops.itg", password_hash=hash_password("ChangeMe123!"), role="admin"))
        await db.commit()
        print("Admin dibuat: admin@labops.itg / ChangeMe123! (ganti segera)")

async def seed_labs():
    path = TEMPLATES / "labs.csv"
    if not path.exists():
        print("labs.csv tidak ditemukan, skip.")
        return
    async with SessionLocal() as db:
        from sqlalchemy import select
        import json
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                exists = (await db.execute(select(Lab).where(Lab.canonical_name == row["canonical_name"]))).scalar_one_or_none()
                if exists:
                    continue
                aliases = [a.strip() for a in row.get("aliases", "").split(";") if a.strip()]
                facilities = [x.strip() for x in row.get("facilities", "").split(";") if x.strip()]
                capabilities = [x.strip() for x in row.get("capabilities", "").split(";") if x.strip()]
                db.add(Lab(canonical_name=row["canonical_name"], aliases=aliases, capacity=int(row.get("capacity", 30)),
                            facilities=facilities, capabilities=capabilities, status=row.get("status", "aktif")))
        await db.commit()
    print("Lab di-seed dari labs.csv")

async def seed_components():
    path = TEMPLATES / "components.csv"
    if not path.exists():
        print("components.csv tidak ditemukan, skip.")
        return
    async with SessionLocal() as db:
        from sqlalchemy import select
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                exists = (await db.execute(select(Component).where(Component.name == row["name"]))).scalar_one_or_none()
                if exists:
                    continue
                db.add(Component(name=row["name"], category=row["category"], unit=row["unit"],
                                 is_consumable=row.get("is_consumable", "false").lower() == "true",
                                 min_stock=int(row.get("min_stock", 0))))
        await db.commit()
    print("Komponen di-seed dari components.csv")

async def main():
    print("Menjalankan seed master data (M0)...")
    await seed_admin()
    await seed_labs()
    await seed_components()
    print("Seed selesai. Lanjutkan dengan impor data (unit, jadwal, konten) via aplikasi.")

if __name__ == "__main__":
    asyncio.run(main())