"""
Configuration module for the Agentic Honeypot System.
Handles environment variables and application settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    HONEYPOT_API_KEY: str = "hp-secret-key-2026"
    API_TITLE: str = "Agentic Honeypot API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered scam detection and autonomous engagement system"
    
    # OpenAI / LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    
    # Fallback to Google Gemini if OpenAI is not available
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Groq Configuration
    GROQ_API_KEY: Optional[str] = None
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def API_KEY(self) -> str:
        """Alias for HONEYPOT_API_KEY."""
        return self.HONEYPOT_API_KEY
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Returns cached application settings."""
    return Settings()
