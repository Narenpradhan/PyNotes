# Authored by Naren Pradhan (https://github.com/Narenpradhan)
# PyNotes: Two-Tier Containerized Application Deployment in Kubernetes

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from app.database import client
from app.routes import router as notes_router

# State flag to track startup status
app_state = {"started": False}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle
    app_state["started"] = True
    yield
    # Shutdown lifecycle: Close MongoDB connection gracefully
    client.close()


app = FastAPI(
    title="Note-Taking API",
    description="A simple FastAPI & MongoDB backend for note-taking. Perfect for Docker and Kubernetes practice.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routes
app.include_router(notes_router)


@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Welcome to the Note-Taking API!",
        "docs_url": "/docs",
        "health_url": "/health",
        "probes": {
            "liveness": "/health/live",
            "readiness": "/health/ready",
            "startup": "/health/startup",
        },
    }


# ==========================================
# Kubernetes Probes & Health Checks
# ==========================================


@app.get("/health", tags=["Probes"])
async def general_health():
    """General health check endpoint."""
    return {"status": "healthy"}


@app.get("/health/live", tags=["Probes"])
@app.get("/livez", tags=["Probes"])
async def liveness_probe():
    """
    Liveness Probe:
    Checks if the application container/process is alive and running.
    If this fails, Kubernetes restarts the pod.
    """
    return {"status": "alive"}


@app.get("/health/ready", tags=["Probes"])
@app.get("/readyz", tags=["Probes"])
async def readiness_probe():
    """
    Readiness Probe:
    Checks if the application is ready to accept user traffic.
    Verifies that the database is reachable.
    If this fails, Kubernetes removes the pod from service endpoints.
    """
    try:
        # Ping MongoDB database with a short timeout
        await client.admin.command("ping")
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not ready", "database": "disconnected", "error": str(exc)},
        )


@app.get("/health/startup", tags=["Probes"])
@app.get("/startupz", tags=["Probes"])
async def startup_probe():
    """
    Startup Probe:
    Checks if the application startup sequence has completed.
    Kubernetes waits for this to succeed before running liveness/readiness probes.
    """
    if not app_state.get("started", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "starting", "message": "Application is still initializing"},
        )
    try:
        await client.admin.command("ping")
        return {"status": "started", "database": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "starting", "database": "not yet reachable", "error": str(exc)},
        )

