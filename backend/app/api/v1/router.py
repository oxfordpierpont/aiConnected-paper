"""API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1 import auth, agencies, clients, documents, generation, schedule, templates

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agencies.router, prefix="/agencies", tags=["Agencies"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(generation.router, prefix="/generation", tags=["Generation"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
