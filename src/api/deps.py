from typing import Generator
from ..services.message_service import MessageService
from ..services.thread_service import ThreadService
from ..services.openai_service import OpenAIService
from ..db.neo4j import Neo4jService

def get_neo4j_service() -> Generator[Neo4jService, None, None]:
    service = Neo4jService()
    try:
        yield service
    finally:
        service.close()

def get_message_service() -> MessageService:
    return MessageService()

def get_thread_service() -> ThreadService:
    return ThreadService()

def get_openai_service() -> OpenAIService:
    return OpenAIService()