import pytest
from fastapi.testclient import TestClient
from typing import Generator
from src.main import app
from src.db.neo4j import Neo4jService
from src.services.message_service import MessageService
from src.services.thread_service import ThreadService
from src.core.config import get_settings

@pytest.fixture
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture
def neo4j_service() -> Generator:
    service = Neo4jService()
    try:
        yield service
    finally:
        service.close()

@pytest.fixture(autouse=True)
def neo4j_cleanup():
    neo4j_service = Neo4jService()
    with neo4j_service.get_session() as session:
        yield session
        # Cleanup after each test
        session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))
