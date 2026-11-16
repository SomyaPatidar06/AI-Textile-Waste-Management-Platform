"""
Sliding-Window In-Memory Rate Limiter.

Protects sensitive endpoints (e.g. login brute-force, heavy model scanning)
against denial-of-service and credential-stuffing attacks without requiring
external Redis dependencies for local and single-node production setups.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Tuple
from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._records: Dict[str, deque] = defaultdict(deque)

    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            timestamps = self._records[key]
            # Prune timestamps outside current window
            while timestamps and timestamps[0] < window_start:
                timestamps.popleft()

            if len(timestamps) >= max_requests:
                oldest = timestamps[0]
                retry_after = max(1, int(window_seconds - (now - oldest)))
                return False, retry_after

            timestamps.append(now)
            return True, 0

    def reset(self) -> None:
        """Clears all rate limit windows (for testing isolation)."""
        with self._lock:
            self._records.clear()


rate_limiter = SlidingWindowRateLimiter()


def rate_limit_dependency(max_requests: int, window_seconds: int = 60):
    """FastAPI dependency to enforce rate limits per client IP."""
    def dependency(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = f"{client_ip}:{path}"

        allowed, retry_after = rate_limiter.is_allowed(key, max_requests, window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )

    return dependency
