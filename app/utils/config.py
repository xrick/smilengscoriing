import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application configuration"""
    
    # Azure Speech Services
    azure_speech_key: str
    azure_speech_region: str
    
    # OpenAI
    openai_api_key: str
    
    # Application settings
    debug: bool = False
    log_level: str = "INFO"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings