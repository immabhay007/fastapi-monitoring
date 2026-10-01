from fastapi import Header, HTTPException, status
from .metrics import AUTH_FAILURES

API_KEY = "secret-api-key-123"

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        AUTH_FAILURES.labels(endpoint="/secure").inc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return x_api_key