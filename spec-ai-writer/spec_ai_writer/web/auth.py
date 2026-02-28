"""API key authentication dependency for FastAPI."""

import logging
import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config.settings import get_settings

logger = logging.getLogger(__name__)

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_auth_warning_logged = False


async def verify_api_key(
    api_key: Optional[str] = Security(_api_key_header),
) -> Optional[str]:
    """
    FastAPI dependency that verifies the API key.

    If API_KEY is not set, auth is skipped (warning logged once).
    If API_KEY is set, the request must include a matching X-API-Key header.
    """
    global _auth_warning_logged
    settings = get_settings()

    if not settings.api_key:
        if not _auth_warning_logged:
            logger.warning(
                "API_KEY is not set. All endpoints are unauthenticated. "
                "Set the API_KEY environment variable to enable authentication."
            )
            _auth_warning_logged = True
        return None

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide it via the X-API-Key header.",
        )

    if not secrets.compare_digest(api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return api_key
