# app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "TrustGate"
    VERSION: str = "0.1.0"
    MODE: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    """Cache settings to avoid repeated file reads."""
    return Settings()

if __name__ == "__main__":
    settings = get_settings()
    print(settings.model_dump())
