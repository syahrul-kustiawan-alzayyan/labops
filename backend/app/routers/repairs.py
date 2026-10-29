from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.deps import get_db, require_admin
from app.services.repairs_service import RepairsService

router = APIRouter(prefix="/repairs", tags=["repairs"])

def svc(db, user):
    return RepairsService(db, user.id)

@router.get("/tickets")
async def list_tickets(status: str | None = None, priority: str | None = None,
                      db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_tickets(status, priority)

@router.post("/tickets")
async def create_ticket(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_ticket(data)

@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_ticket(ticket_id)

@router.post("/tickets/{ticket_id}/triage")
async def triage(ticket_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).triage(ticket_id, data["result"], data.get("note"))

@router.post("/tickets/{ticket_id}/actions")
async def add_action(ticket_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).add_action(ticket_id, data)

@router.post("/tickets/{ticket_id}/verify")
async def verify(ticket_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).verify(ticket_id, data["result"], data.get("test_notes", ""))

@router.get("/vendors")
async def list_vendors(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_vendors()
@router.post("/vendors")
async def create_vendor(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_vendor(data)

@router.put("/vendors/{vendor_id}")
async def update_vendor(vendor_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).update_vendor(vendor_id, data)

@router.delete("/vendors/{vendor_id}")
async def delete_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).delete_vendor(vendor_id)
