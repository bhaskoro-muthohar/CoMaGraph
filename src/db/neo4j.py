from neo4j import GraphDatabase
from ..core.config import get_settings
from contextlib import contextmanager

class Neo4jService:
    def __init__(self):
        self.settings = get_settings()
        self._driver = GraphDatabase.driver(
            self.settings.NEO4J_URI,
            auth=(self.settings.NEO4J_USER, self.settings.NEO4J_PASSWORD)
        )

    @contextmanager
    def get_session(self):
        session = self._driver.session()
        try:
            yield session
        finally:
            session.close()

    def close(self):
        self._driver.close()

    def init_constraints(self):
        """Initialize Neo4j constraints and indexes"""
        with self.get_session() as session:
            # Create constraints for Message nodes
            session.run("""
                CREATE CONSTRAINT message_id IF NOT EXISTS 
                FOR (m:Message) REQUIRE m.id IS UNIQUE
            """)
            
            # Create constraints for Thread nodes
            session.run("""
                CREATE CONSTRAINT thread_id IF NOT EXISTS 
                FOR (t:Thread) REQUIRE t.id IS UNIQUE
            """)