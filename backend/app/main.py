import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base
import app.models
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.reports import router as reports_router

# Setup structured logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("textile_platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Application initialized. Database schemas and upload storage ready.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Textile waste characterization, circularity assessment, and recycling platform.",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_correlation_and_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    t0 = time.perf_counter()

    try:
        response: Response = await call_next(request)
        latency_ms = (time.perf_counter() - t0) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} "
            f"({latency_ms:.2f}ms) [rid={request_id}]"
        )
        return response
    except Exception as exc:
        latency_ms = (time.perf_counter() - t0) * 1000
        logger.exception(f"Unhandled exception during {request.method} {request.url.path} [rid={request_id}]: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error. Please contact administrator.",
                "request_id": request_id
            },
            headers={"X-Request-ID": request_id}
        )


@app.get("/health", tags=["System Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["System Health"])
def health_check():
    """Comprehensive high-level system health and configuration status."""
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {
        "status": "healthy" if "disconnected" not in db_status else "degraded",
        "version": "2.1.0",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "models": {
            "material_version": settings.MATERIAL_MODEL_VERSION,
            "defect_version": settings.DEFECT_MODEL_VERSION,
            "defect_threshold": settings.DEFECT_CONFIDENCE_THRESHOLD,
        }
    }


@app.get("/health/ready", tags=["System Health"])
@app.get(f"{settings.API_V1_STR}/health/ready", tags=["System Health"])
def readiness_probe():
    """Readiness probe checking database connectivity, storage, and AI model checkpoints."""
    checks: Dict[str, Any] = {}
    is_ready = True

    # 1. Database check
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ready"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        is_ready = False

    # 2. Storage writeability check
    try:
        upload_path = Path(settings.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        test_file = upload_path / ".readiness_probe"
        test_file.write_text("probe", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        checks["storage"] = "writable"
    except Exception as e:
        checks["storage"] = f"unhealthy: {str(e)}"
        is_ready = False

    # 3. Model checkpoint presence and integrity verification
    try:
        from app.ai.model_verifier import verify_models
        model_audit = verify_models()
        checks["ai_models"] = "loaded" if model_audit["all_primary_present"] else "missing_weights"
        checks["ai_verification"] = {
            "status": model_audit["status"],
            "all_primary_present": model_audit["all_primary_present"],
            "all_hashes_verified": model_audit["all_hashes_verified"],
            "checkpoints": {
                k: {"status": v["status"], "size": v.get("size_bytes")}
                for k, v in model_audit["checkpoints"].items()
            }
        }
        if not model_audit["all_primary_present"]:
            is_ready = False
            checks["ai_verification"]["instructions"] = model_audit["remediation_instructions"]
    except Exception as e:
        checks["ai_models"] = "missing_weights"
        checks["ai_verification"] = f"verification_error: {str(e)}"
        is_ready = False

    if not is_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks}
        )

    return {"status": "ready", "checks": checks}


@app.get("/health/live", tags=["System Health"])
@app.get(f"{settings.API_V1_STR}/health/live", tags=["System Health"])
def liveness_probe():
    """Liveness probe confirming API service execution."""
    return {"status": "alive", "timestamp": time.time()}


app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(inventory_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
