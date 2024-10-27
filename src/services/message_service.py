from typing import List, Optional
from uuid import UUID
from ..models.message import Message, MessageCreate
from ..db.neo4j import Neo4jService
from ..services.openai_service import OpenAIService
from ..core.config import get_settings
from ..core.exceptions import ContextManagerException, DatabaseConnectionError
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MessageService:
    def __init__(self):
        self.neo4j = Neo4jService()
        self.openai = OpenAIService()
        self.settings = get_settings()

    async def create_message(self, message_create: MessageCreate) -> Message:
        """Create a new message with embedding and store in Neo4j"""
        try:
            logger.debug(f"Starting message creation with content: {message_create.content}")
        
            # First, verify thread exists
            with self.neo4j.get_session() as session:
                logger.debug(f"Verifying thread existence for ID: {message_create.thread_id}")
                thread_exists = session.execute_read(
                    lambda tx: tx.run(
                        "MATCH (t:Thread {id: $thread_id}) RETURN count(t) as count",
                        thread_id=str(message_create.thread_id)
                    ).single()["count"]
                )
            
                if not thread_exists:
                    raise ContextManagerException(f"Thread {message_create.thread_id} not found")

            # Generate embedding
            embedding = await self.openai.generate_embedding(message_create.content)
        
            # Create message instance
            message = Message(
                content=message_create.content,
                role=message_create.role,
                thread_id=message_create.thread_id,
                embedding=embedding,
                metadata=message_create.metadata
            )
        
            # Store in Neo4j - metadata stored as individual properties
            with self.neo4j.get_session() as session:
                result = session.execute_write(
                    lambda tx: tx.run(
                        """
                        MATCH (t:Thread {id: $thread_id})
                        CREATE (m:Message {
                            id: $id,
                            content: $content,
                            role: $role,
                            created_at: datetime(),
                            embedding: $embedding
                        })-[:BELONGS_TO]->(t)
                        RETURN m
                        """,
                        id=str(message.id),
                        content=message.content,
                        role=message.role,
                        thread_id=str(message.thread_id),
                        embedding=message.embedding
                    ).single()
                )
            
                if not result:
                    raise DatabaseConnectionError("Failed to create message in database")
            
                return message
                
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}", exc_info=True)
            raise ContextManagerException(f"Failed to create message: {str(e)}")

    async def get_thread_context(
        self, 
        thread_id: UUID,
        message_id: Optional[UUID] = None,
        window_size: Optional[int] = None
    ) -> List[Message]:
        """Get context from thread, optionally centered around a specific message"""
        if window_size is None:
            window_size = self.settings.CONTEXT_WINDOW_SIZE
            
        with self.neo4j.get_session() as session:
            if message_id:
                with session.begin_transaction() as tx:
                    result = tx.run("""
                        MATCH (m:Message {id: $message_id})-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                        MATCH (context:Message)-[:BELONGS_TO]->(t)
                        WHERE abs(duration.between(context.created_at, m.created_at).seconds) <= $window_seconds
                        RETURN {
                            id: toString(context.id),
                            content: context.content,
                            role: context.role,
                            created_at: toString(context.created_at),
                            thread_id: toString(t.id),
                            metadata: coalesce(context.metadata, {})
                        } as context
                        ORDER BY context.created_at
                    """,
                    message_id=str(message_id),
                    thread_id=str(thread_id),
                    window_seconds=window_size * 60
                    )
                    messages = [Message.model_validate(record["context"]) for record in result]
            else:
                with session.begin_transaction() as tx:
                    result = tx.run("""
                        MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                        RETURN {
                            id: toString(m.id),
                            content: m.content,
                            role: m.role,
                            created_at: toString(m.created_at),
                            thread_id: toString(t.id),
                            metadata: coalesce(m.metadata, {})
                        } as m
                        ORDER BY m.created_at DESC
                        LIMIT $limit
                    """,
                    thread_id=str(thread_id),
                    limit=window_size
                    )
                    messages = [Message.model_validate(record["m"]) for record in result]
        
        return messages