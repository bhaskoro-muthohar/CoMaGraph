from typing import List, Optional
from uuid import UUID
from ..models.message import Message, MessageCreate
from ..db.neo4j import Neo4jService
from ..services.openai_service import OpenAIService
from ..core.config import get_settings

class MessageService:
    def __init__(self):
        self.neo4j = Neo4jService()
        self.openai = OpenAIService()
        self.settings = get_settings()

    async def create_message(self, message_create: MessageCreate) -> Message:
        """Create a new message with embedding and store in Neo4j"""
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
        
        # Store in Neo4j
        with self.neo4j.get_session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    MessageQueries.CREATE_MESSAGE,
                    id=str(message.id),
                    content=message.content,
                    role=message.role,
                    thread_id=str(message.thread_id),
                    embedding=message.embedding,
                    metadata=message.metadata
                )
            )
        
        return message

    async def get_similar_messages(
        self, 
        content: str, 
        limit: int = 5
    ) -> List[Message]:
        """Find similar messages based on content"""
        # Generate embedding for query content
        query_embedding = await self.openai.generate_embedding(content)
        
        # Query Neo4j for similar messages using vector similarity
        with self.neo4j.get_session() as session:
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (m:Message)
                    WITH m, gds.similarity.cosine(m.embedding, $embedding) AS score
                    WHERE score >= $threshold
                    RETURN m
                    ORDER BY score DESC
                    LIMIT $limit
                """,
                embedding=query_embedding,
                threshold=self.settings.SIMILARITY_THRESHOLD,
                limit=limit
                )
            )
            
            messages = [
                Message.model_validate(record["m"])
                for record in result
            ]
        
        return messages

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
                # Get context around specific message
                result = session.execute_read(
                    lambda tx: tx.run("""
                        MATCH (m:Message {id: $message_id})-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                        MATCH (context:Message)-[:BELONGS_TO]->(t)
                        WHERE abs(duration.between(context.created_at, m.created_at).seconds) <= $window_seconds
                        RETURN context
                        ORDER BY context.created_at
                    """,
                    message_id=str(message_id),
                    thread_id=str(thread_id),
                    window_seconds=window_size * 60  # Convert minutes to seconds
                    )
                )
            else:
                # Get most recent context
                result = session.execute_read(
                    lambda tx: tx.run("""
                        MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                        RETURN m
                        ORDER BY m.created_at DESC
                        LIMIT $limit
                    """,
                    thread_id=str(thread_id),
                    limit=window_size
                    )
                )
            
            messages = [
                Message.model_validate(record["m" if message_id else "context"])
                for record in result
            ]
        
        return messages