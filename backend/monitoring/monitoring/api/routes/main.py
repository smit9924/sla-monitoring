from fastapi import APIRouter

from monitoring.api.routes import health

api_router = APIRouter()
api_router.include_router(health.router)
