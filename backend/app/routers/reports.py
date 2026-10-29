from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, require_admin
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])

def svc(db):
    return ReportsService(db)

@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db).dashboard()

@router.get("/inventory")
async def inventory_report(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db).inventory_report()

@router.get("/repairs")
async def repair_report(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db).repair_report()

@router.get("/usage")
async def usage_report(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db).usage_report()

@router.get("/social")
async def social_report(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db).social_report()

@router.post("/monthly")
async def monthly_report(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    from datetime import date as d
    ps = d.fromisoformat(data["period_start"])
    pe = d.fromisoformat(data["period_end"])
    return await svc(db).monthly_report(ps, pe)