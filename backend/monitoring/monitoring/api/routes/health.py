import logging

from fastapi import APIRouter

from monitoring.core.config import settings
from monitoring.doc.health_exceptions_doc import HEALTH_EXCEPTIONS_DOC
from monitoring.exceptions.definitions.health_exceptions import (
    ServiceUnavailableException,
)
from monitoring.schemas.health_schemas import HealthCheckResponse

log = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    responses={**HEALTH_EXCEPTIONS_DOC["ServiceUnavailableException"]},
)
async def health_check() -> HealthCheckResponse:
    """
    Report whether the service is up and able to serve traffic.
    """
    try:
        return HealthCheckResponse(
            status="ok",
            service=settings.SERVICE_NAME,
            environment=settings.ENVIRONMENT,
        )
    except Exception:
        log.exception("Health check failed")
        raise ServiceUnavailableException()
