from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    MULTIPLE_PROMPT_PROB: float = os.getenv("MULTIPLE_PROMPT_PROB", 0.3)

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 