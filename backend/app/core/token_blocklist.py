"""
Thread-safe Token Blocklist and Revocation Manager.

Maintains revoked JWT IDs (jti) for access and refresh token revocation,
rotation enforcement, and logout protection.
"""

import threading
import time
from typing import Dict


class TokenBlocklistManager:
    """In-memory thread-safe blocklist with automatic TTL cleanup."""

    def __init__(self):
        self._lock = threading.Lock()
        self._revoked_tokens: Dict[str, float] = {}

    def revoke_token(self, jti: str, exp: float) -> None:
        """Revokes a token identifier until its expiration timestamp."""
        with self._lock:
            self._revoked_tokens[jti] = exp
            self._prune_expired()

    def is_token_revoked(self, jti: str) -> bool:
        """Checks if a token identifier has been revoked."""
        if not jti:
            return False
        with self._lock:
            now = time.time()
            exp = self._revoked_tokens.get(jti)
            if exp is None:
                return False
            if exp < now:
                # Expired naturally, remove from blocklist
                del self._revoked_tokens[jti]
                return False
            return True

    def _prune_expired(self) -> None:
        now = time.time()
        to_del = [jti for jti, exp in self._revoked_tokens.items() if exp < now]
        for jti in to_del:
            del self._revoked_tokens[jti]

    def clear(self) -> None:
        """Clears all revoked tokens (for testing isolation)."""
        with self._lock:
            self._revoked_tokens.clear()


token_blocklist = TokenBlocklistManager()
