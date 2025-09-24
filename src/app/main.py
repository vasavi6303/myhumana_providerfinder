import os
import time
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from .healthpilot_client import HealthpilotClient
from .models import SearchRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("providerfinder")

app = FastAPI(title="Provider Finder Service", version="1.0.0")

# CORS - allow list can be configured via env
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hp_client = HealthpilotClient()

# Prometheus metrics
REQUEST_COUNT = Counter("providerfinder_requests_total", "Total HTTP requests", ["method","path","status"])
HP_LATENCY = Histogram("healthpilot_request_latency_seconds", "Healthpilot API latency seconds")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency (s)", ["path"])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception as e:
        status = 500
        logger.exception("Unhandled error")
        raise
    finally:
        elapsed = time.time() - start
        REQUEST_LATENCY.labels(path=request.url.path).observe(elapsed)
        REQUEST_COUNT.labels(method=request.method, path=request.url.path, status=str(status)).inc()
    return response

@app.get('/metrics')
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get('/health')
def health():
    return {"status": "ok"}

@app.post('/search')
async def search(req: SearchRequest):
    try:
        with HP_LATENCY.time():
            providers = await hp_client.search_providers(query=req.query, location=req.location, specialty=req.specialty)
        return {"count": len(providers), "providers": providers}
    except Exception as e:
        logger.exception("Healthpilot search failed")
        raise HTTPException(status_code=502, detail="upstream search failed") from e
