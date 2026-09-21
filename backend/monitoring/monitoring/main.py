from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from monitoring.api.routes.main import api_router
from monitoring.core.config import settings
from monitoring.exceptions.registry import get_exception_handlers
from monitoring.logging import configure_logging
from monitoring.middleware import REQUEST_ID_HEADER, RequestContextMiddleware

configure_logging(settings.logging_settings())

exception_handlers = get_exception_handlers()

app = FastAPI(
    title=settings.app_name,
    exception_handlers=exception_handlers,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
    expose_headers=[REQUEST_ID_HEADER],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
