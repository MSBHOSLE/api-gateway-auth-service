from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.gateway import router as gateway_router
from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Redis
    try:
        await init_db()
    except Exception as e:
        print(f"Database init warning: {e}")
    await rate_limiter.connect()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="High-performance API Gateway with JWT RBAC authentication and Redis-backed sliding window rate limiting.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(gateway_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": settings.APP_NAME}
