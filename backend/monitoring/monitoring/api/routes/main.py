from fastapi import APIRouter

from monitoring.api.routes import files, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(files.router)
