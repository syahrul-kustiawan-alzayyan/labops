from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.deps import get_db, require_admin
from app.models.core import ActivityLog, Setting, Notification

router = APIRouter(prefix="/core", tags=["core"])

@router.get("/activity-logs")
async def activity_logs(limit: int = 50, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    r = await db.execute(select(ActivityLog).order_by(ActivityLog.occurred_at.desc()).limit(limit))
    return list(r.scalars().all())

@router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    r = await db.execute(select(Setting))
    return list(r.scalars().all())

@router.put("/settings/{key}")
async def update_setting(key: str, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    from sqlalchemy import insert
    existing = (await db.execute(select(Setting).where(Setting.key == key))).scalar_one_or_none()
    if existing:
        existing.value = data.get("value")
        await db.commit()
        await db.refresh(existing)
        return existing
    s = Setting(key=key, value=data.get("value"))
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s

@router.get("/notifications")
async def notifications(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    r = await db.execute(select(Notification).order_by(Notification.created_at.desc()).limit(50))
    return list(r.scalars().all())