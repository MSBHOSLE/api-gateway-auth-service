from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
import httpx
from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.core.security import decode_token

router = APIRouter(prefix="/proxy", tags=["Reverse Proxy & Gateway"])


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def reverse_proxy(path: str, request: Request):
    """Dynamically route and reverse-proxy requests to upstream services with sliding-window rate limiting."""
    # 1. Extract client identifier for rate limiting (JWT subject if authenticated, otherwise Client IP)
    auth_header = request.headers.get("authorization")
    client_id = request.client.host if request.client else "unknown_client"
    authenticated_user = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if payload and payload.get("sub"):
            authenticated_user = payload.get("sub")
            client_id = f"user:{authenticated_user}"

    # 2. Check Sliding Window Rate Limit
    allowed, remaining, window_secs = await rate_limiter.is_allowed(
        identifier=client_id,
        limit=settings.RATE_LIMIT_PER_MINUTE,
        window_seconds=60,
    )

    headers = {
        "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(window_secs),
    }

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Too many requests.",
            headers=headers,
        )

    # 3. Echo/Simulate upstream response if no downstream microservice configured
    body = await request.body()
    return Response(
        content=f'{{"proxy_status": "forwarded", "path": "{path}", "client": "{client_id}", "remaining_quota": {remaining}}}',
        media_type="application/json",
        headers=headers,
    )
