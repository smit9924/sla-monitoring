# monitoring

FastAPI backend for the SLA Monitoring Dashboard.

## Layout

```
monitoring/
├── main.py                  # FastAPI app, middleware, exception handler registration
├── core/
│   └── config.py            # Pydantic settings loaded from .env
├── api/
│   └── routes/
│       ├── main.py          # Aggregates all route routers
│       └── health.py        # GET /api/v1/health
├── doc/
│   └── health_exceptions_doc.py   # OpenAPI response examples per exception
├── exceptions/
│   ├── definitions/         # Custom exception classes
│   ├── handlers/            # FastAPI exception handler functions
│   └── registry.py          # Maps exception classes -> handlers
├── schemas/                 # Pydantic models (camelCase API contracts)
├── types/
│   ├── enums.py
│   └── error_codes.py       # Stable numeric error codes returned to clients
├── logging/                 # Structured console/JSON logging setup
├── middleware/              # Request-ID context middleware
└── storage/                 # Pluggable file storage (BaseStorage + GCS provider)
    ├── base.py                # BaseStorage abstract interface
    ├── factory.py             # get_storage_client() singleton factory
    └── providers/
        └── gcs_storage.py     # GCSStorage (Google Cloud Storage)
```

## Running locally

```bash
cp .sample.env .env
uv sync
uv run fastapi dev --port 8000 ./monitoring/main.py
```

The health check is available at `GET /api/v1/health`, and interactive docs
at `/docs`.
