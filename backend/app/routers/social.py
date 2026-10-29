from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date as d
from app.core.deps import get_db, require_admin
from app.services.social_service import SocialService

router = APIRouter(prefix="/social", tags=["social"])

def svc(db, user):
    return SocialService(db, user.id)

@router.get("/accounts")
async def list_accounts(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_accounts()

@router.post("/accounts")
async def create_account(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_account(data)

@router.get("/contents")
async def list_contents(account_id: UUID | None = None, status: str | None = None,
                       db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_contents(account_id, status)

@router.post("/contents")
async def create_content(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_content(data)

@router.get("/contents/{content_id}")
async def get_content(content_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_content(content_id)

@router.put("/contents/{content_id}")
async def update_content(content_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).update_content(content_id, data)

@router.get("/contents/{content_id}/checklist")
async def get_checklist(content_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_checklist(content_id)

@router.put("/contents/{content_id}/checklist")
async def update_checklist(content_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).update_checklist(content_id, data["items"])

@router.post("/contents/{content_id}/approve")
async def approve(content_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).approve(content_id, user.id)

@router.post("/contents/{content_id}/schedule")
async def schedule(content_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    sd = d.fromisoformat(data["date"])
    from datetime import time as t
    st = t.fromisoformat(data["time"]) if data.get("time") else None
    return await svc(db, user).schedule(content_id, sd, st)

@router.post("/contents/{content_id}/mark-posted")
async def mark_posted(content_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).mark_posted(content_id)

@router.post("/contents/{content_id}/reopen")
async def reopen(content_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).reopen(content_id)

@router.post("/contents/{content_id}/cancel")
async def cancel(content_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).cancel_content(content_id, data.get("reason"))

@router.get("/calendar")
async def calendar(month: int, year: int, account_id: UUID | None = None,
                  db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_calendar(month, year, account_id)

@router.get("/due")
async def due_list(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_due_list()

@router.post("/migrate")
async def migrate(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).migrate_legacy(data["rows"])