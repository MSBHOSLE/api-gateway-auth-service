import asyncio
import unittest
from app.core.rate_limiter import SlidingWindowRateLimiter


class TestRateLimiter(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Force in-memory limiter for isolation
        self.limiter = SlidingWindowRateLimiter(redis_url=None)

    async def test_sliding_window_allows_within_limit(self):
        client = "192.168.1.100"
        for i in range(5):
            allowed, remaining, _ = await self.limiter.is_allowed(client, limit=5, window_seconds=10)
            self.assertTrue(allowed)

        # 6th request should be rejected
        allowed, remaining, _ = await self.limiter.is_allowed(client, limit=5, window_seconds=10)
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)

    async def test_sliding_window_resets_after_window(self):
        client = "192.168.1.200"
        allowed, _, _ = await self.limiter.is_allowed(client, limit=1, window_seconds=1)
        self.assertTrue(allowed)

        # Immediate repeat should fail
        allowed, _, _ = await self.limiter.is_allowed(client, limit=1, window_seconds=1)
        self.assertFalse(allowed)

        # Wait for 1.1s window expiry
        await asyncio.sleep(1.1)
        allowed, _, _ = await self.limiter.is_allowed(client, limit=1, window_seconds=1)
        self.assertTrue(allowed)


if __name__ == "__main__":
    unittest.main()
