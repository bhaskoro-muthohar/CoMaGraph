# src/services/thread_service.py
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from ..models.thread import Thread, ThreadCreate, ThreadSummary
from ..models.message import Message
from ..db.neo4j import Neo4jService
from ..services.openai_service import OpenAIService
from ..core.config import get_settings
from ..core.exceptions import ThreadNotFoundError
from ..core.constants import ThreadStatus

class ThreadService:
    def __init__(self):
        self.neo4j = Neo4jService()
        self.openai = OpenAIService()
        self.settings = get_settings()

    async def create_thread(self, thread_create: ThreadCreate) -> Thread:
        """Create a new conversation thread"""
        thread = Thread(
            metadata=thread_create.metadata
        )

        with self.neo4j.get_session() as session:
            session.execute_write(
                lambda tx: tx.run("""
                    CREATE (t:Thread {
                        id: $id,
                        status: $status,
                        created_at: datetime(),
                        updated_at: datetime(),
                        metadata: $metadata
                    })
                    RETURN t
                """,
                id=str(thread.id),
                status=thread.status,
                metadata=thread.metadata
                )
            )

        return thread

    async def get_thread(self, thread_id: UUID) -> Thread:
        """Retrieve a thread by ID"""
        with self.neo4j.get_session() as session:
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (t:Thread {id: $thread_id})
                    RETURN t
                """,
                thread_id=str(thread_id)
                )
            ).single()

            if not result:
                raise ThreadNotFoundError(f"Thread {thread_id} not found")

            thread_data = result["t"]
            return Thread.model_validate(thread_data)

    async def update_thread_status(
        self,
        thread_id: UUID,
        status: str
    ) -> Thread:
        """Update thread status (active/archived)"""
        if status not in [ThreadStatus.ACTIVE, ThreadStatus.ARCHIVED]:
            raise ValueError(f"Invalid status: {status}")

        with self.neo4j.get_session() as session:
            result = session.execute_write(
                lambda tx: tx.run("""
                    MATCH (t:Thread {id: $thread_id})
                    SET t.status = $status,
                        t.updated_at = datetime()
                    RETURN t
                """,
                thread_id=str(thread_id),
                status=status
                )
            ).single()

            if not result:
                raise ThreadNotFoundError(f"Thread {thread_id} not found")

            return Thread.model_validate(result["t"])

    async def get_thread_summary(self, thread_id: UUID) -> ThreadSummary:
        """Generate a summary of the thread including topics and analytics"""
        with self.neo4j.get_session() as session:
            # Get all messages in thread
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                    RETURN m
                    ORDER BY m.created_at
                """,
                thread_id=str(thread_id)
                )
            )

            messages = [Message.model_validate(record["m"]) for record in result]

            if not messages:
                raise ThreadNotFoundError(f"Thread {thread_id} not found or empty")

            # Extract topics from all messages
            all_content = " ".join([msg.content for msg in messages])
            topics = await self.openai.extract_topics(all_content)

            # Generate summary
            summary = await self.openai.summarize_thread(
                [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ]
            )

            return ThreadSummary(
                id=thread_id,
                message_count=len(messages),
                last_message_at=messages[-1].created_at,
                topics=topics,
                summary=summary
            )

    async def get_thread_analytics(
        self,
        thread_id: UUID
    ) -> Dict:
        """Get detailed analytics for a thread"""
        with self.neo4j.get_session() as session:
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                    WITH m, t
                    OPTIONAL MATCH (m)-[r:NEXT]->(next:Message)
                    RETURN 
                        count(m) as message_count,
                        sum(CASE WHEN m.role = 'user' THEN 1 ELSE 0 END) as user_messages,
                        sum(CASE WHEN m.role = 'assistant' THEN 1 ELSE 0 END) as assistant_messages,
                        avg(duration.between(m.created_at, next.created_at).seconds) as avg_response_time
                """,
                thread_id=str(thread_id)
                )
            ).single()

            if not result:
                raise ThreadNotFoundError(f"Thread {thread_id} not found")

            return {
                "message_count": result["message_count"],
                "user_messages": result["user_messages"],
                "assistant_messages": result["assistant_messages"],
                "average_response_time_seconds": result["avg_response_time"]
            }

    async def find_similar_threads(
        self,
        content: str,
        limit: int = 5
    ) -> List[ThreadSummary]:
        """Find similar threads based on message content"""
        # Generate embedding for query content
        query_embedding = await self.openai.generate_embedding(content)

        with self.neo4j.get_session() as session:
            # Find threads with similar messages
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (m:Message)-[:BELONGS_TO]->(t:Thread)
                    WITH m, t, gds.similarity.cosine(m.embedding, $embedding) AS score
                    WHERE score >= $threshold
                    WITH t, max(score) as max_score
                    RETURN DISTINCT t
                    ORDER BY max_score DESC
                    LIMIT $limit
                """,
                embedding=query_embedding,
                threshold=self.settings.SIMILARITY_THRESHOLD,
                limit=limit
                )
            )

            threads = []
            for record in result:
                thread_id = UUID(record["t"]["id"])
                # Get summary for each similar thread
                summary = await self.get_thread_summary(thread_id)
                threads.append(summary)

            return threads