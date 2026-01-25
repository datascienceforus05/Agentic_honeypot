"""
Security Module.
Handles API key validation and security middleware.
"""

import logging
import secrets
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import get_settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name="x-api-key", auto_error=False)


async def validate_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> str:
    """Validate the API key from the request header."""
    settings = get_settings()
    
    if api_key is None:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Missing API key", "message": "Provide x-api-key header"}
        )
    
    if not secrets.compare_digest(api_key, settings.API_KEY):
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Invalid API key"}
        )
    
    return api_key


def generate_api_key(length: int = 32) -> str:
    """Generate a new secure API key."""
    return f"hp-{secrets.token_urlsafe(length)}"
