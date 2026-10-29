from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.routers import auth, inventory, repairs, scheduling, social, reports, core

app = FastAPI(
    title="LabOps ITG API",
    version="1.0.0",
    description="Aplikasi operasional laboratorium Ilmu Komputer ITG",
    docs_url="/docs" if settings.ENV != "prod" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

for r in (auth, inventory, repairs, scheduling, social, reports, core):
    app.include_router(r.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV}