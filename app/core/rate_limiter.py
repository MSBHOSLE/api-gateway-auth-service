import time
from typing import Dict, List, Optional, Tuple
import uuid

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from app.core.config import settings


class SlidingWindowRateLimiter:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.client: Optional[Any] = None
        # In-memory fallback dictionary: identifier -> list of timestamp floats
        self._memory_store: Dict[str, List[float]] = {}

    async def connect(self) -> None:
        if redis and self.redis_url and not self.client:
            try:
                self.client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
                await self.client.ping()
            except Exception:
                self.client = None

    async def is_allowed(
        self,
        identifier: str,
        limit: int = 60,
        window_seconds: int = 60,
    ) -> Tuple[bool, int, int]:
        """Check whether request is allowed using sliding window algorithm.

        Returns:
            Tuple of:
            - allowed: bool
            - remaining: int (requests left in current window)
            - reset_time_seconds: int (seconds until window fully resets)
        """
        now = time.time()
        clear_before = now - window_seconds

        # 1. Use Redis if connected
        if self.client:
            try:
                key = f"ratelimit:{identifier}"
                req_id = f"{now}:{uuid.uuid4().hex[:8]}"

                pipe = self.client.pipeline()
                # Remove timestamps older than the sliding window
                pipe.zremrangebyscore(key, 0, clear_before)
                # Count current requests in window
                pipe.zcard(key)
                # Add current request timestamp
                pipe.zadd(key, {req_id: now})
                # Set TTL on the sorted set
                pipe.expire(key, window_seconds + 1)

                results = await pipe.execute()
                current_count = results[1]

                if current_count < limit:
                    remaining = max(0, limit - current_count - 1)
                    return True, remaining, window_seconds
                else:
                    # Over limit: remove the speculative request we added
                    await self.client.zrem(key, req_id)
                    return False, 0, window_seconds
            except Exception:
                pass  # Fall back to in-memory

        # 2. In-Memory Sliding Window Fallback
        timestamps = self._memory_store.get(identifier, [])
        # Prune older than window
        timestamps = [ts for ts in timestamps if ts > clear_before]

        if len(timestamps) < limit:
            timestamps.append(now)
            self._memory_store[identifier] = timestamps
            remaining = limit - len(timestamps)
            return True, remaining, window_seconds
        else:
            self._memory_store[identifier] = timestamps
            return False, 0, window_seconds


rate_limiter = SlidingWindowRateLimiter()
