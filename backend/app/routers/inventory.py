from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.deps import get_db, require_admin
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])

def svc(db, user):
    return InventoryService(db, user.id)

@router.get("/labs")
async def list_labs(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_labs()

@router.post("/labs")
async def create_lab(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_lab(data)

@router.get("/components")
async def list_components(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_components()

@router.post("/components")
async def create_component(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_component(data)

@router.get("/units")
async def list_units(lab_id: UUID | None = None, status: str | None = None, search: str | None = None,
                    db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_units(lab_id, status, search)

@router.post("/units")
async def create_unit(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_unit(data)

@router.get("/units/{unit_id}")
async def get_unit(unit_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_unit(unit_id)

@router.put("/units/{unit_id}/status")
async def update_status(unit_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).update_unit_status(unit_id, data["status"], data.get("reason"))

@router.post("/units/{unit_id}/archive")
async def archive_unit(unit_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).archive_unit(unit_id, data.get("reason"))

@router.post("/units/{unit_id}/verify")
async def verify_unit(unit_id: UUID, data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).verify_unit(unit_id, data["result"], data.get("failed_items"))

@router.get("/checklists")
async def list_checklists(lab_id: UUID | None = None, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).list_checklists(lab_id)

@router.post("/checklists")
async def create_checklist(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    from datetime import date as d
    ld = d.fromisoformat(data["date"])
    return await svc(db, user).create_checklist(UUID(data["lab_id"]), ld, data["items"])

@router.post("/units/import")
async def import_units(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    mode = data.get("mode", "preview")
    rows = data.get("rows", [])
    return await svc(db, user).import_units(rows, mode)

@router.get("/units/{unit_id}/history")
async def unit_history(unit_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_unit_history(unit_id)

@router.get("/units/{unit_id}/tickets")
async def unit_tickets(unit_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).get_unit_tickets(unit_id)

@router.post("/consumables")
async def create_consumable(data: dict, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    return await svc(db, user).create_consumable(data)