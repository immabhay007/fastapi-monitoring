import asyncio
import time
import uuid
import logging
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from .logging_config import setup_logging
from .metrics import RATE_LIMIT_HITS, SERVER_ERRORS, REQUEST_LATENCY
from .auth import verify_api_key

# Setup logging
logger = setup_logging()

app = FastAPI(title="API Monitoring Demo")

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Sample data
USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]

PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Mouse", "price": 19.99},
]

# Middleware for request ID and logging
@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        # Log request
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration": duration,
            }
        )
        # Record latency for custom histogram
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(duration)
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": 500,
                "duration": duration,
            }
        )
        raise

# Endpoints
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/users")
async def get_users():
    return USERS

@app.get("/products")
async def get_products():
    return PRODUCTS

@app.get("/simulate-error")
async def simulate_error():
    SERVER_ERRORS.labels(endpoint="/simulate-error").inc()
    raise HTTPException(status_code=500, detail="Simulated internal server error")

@app.get("/simulate-timeout")
async def simulate_timeout():
    await asyncio.sleep(5)  # Simulate 5 second delay
    return {"message": "This response was delayed by 5 seconds"}

@app.get("/simulate-rate-limit")
async def simulate_rate_limit():
    RATE_LIMIT_HITS.labels(endpoint="/simulate-rate-limit").inc()
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.get("/secure")
async def secure_endpoint(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted", "api_key": api_key}

# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": getattr(request.state, 'request_id', 'unknown')}
    )