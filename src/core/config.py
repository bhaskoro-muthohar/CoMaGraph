from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CoMaGraph"
    
    # Neo4j Config
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # OpenAI Config
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    COMPLETION_MODEL: str = "gpt-3.5-turbo"
    
    # Performance Config
    SIMILARITY_THRESHOLD: float = 0.8
    CONTEXT_WINDOW_SIZE: int = 10
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
