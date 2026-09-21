from .base_schemas import BaseSchema


class HealthCheckResponse(BaseSchema):
    """Response body returned by the health check endpoint."""

    status: str
    service: str
    environment: str
