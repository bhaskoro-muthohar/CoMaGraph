from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
from ..db.neo4j import Neo4jService
from ..services.openai_service import OpenAIService
from ..core.exceptions import ContextManagerException

class AnalysisService:
    def __init__(self):
        self.neo4j = Neo4jService()
        self.openai = OpenAIService()

    async def get_thread_analytics(self, thread_id: UUID) -> Dict[str, Any]:
        """Get comprehensive analytics for a thread"""
        with self.neo4j.get_session() as session:
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                    WITH m, t
                    ORDER BY m.created_at
                    WITH collect(m) as messages, t
                    RETURN {
                        message_count: size(messages),
                        user_messages: size([m in messages WHERE m.role = 'user']),
                        assistant_messages: size([m in messages WHERE m.role = 'assistant']),
                        first_message_time: head(messages).created_at,
                        last_message_time: last(messages).created_at
                    } as stats
                """,
                thread_id=str(thread_id)
                )
            ).single()

            if not result:
                raise ContextManagerException(f"Thread {thread_id} not found")

            stats = result["stats"]
            
            # Calculate duration and activity metrics
            first_message = datetime.fromisoformat(str(stats["first_message_time"]))
            last_message = datetime.fromisoformat(str(stats["last_message_time"]))
            duration = last_message - first_message
            
            return {
                "message_statistics": {
                    "total_messages": stats["message_count"],
                    "user_messages": stats["user_messages"],
                    "assistant_messages": stats["assistant_messages"],
                    "user_message_ratio": stats["user_messages"] / stats["message_count"]
                },
                "time_metrics": {
                    "thread_duration_minutes": duration.total_seconds() / 60,
                    "messages_per_hour": (stats["message_count"] / (duration.total_seconds() / 3600))
                        if duration.total_seconds() > 0 else 0,
                    "first_message": first_message.isoformat(),
                    "last_message": last_message.isoformat()
                }
            }

    async def analyze_conversation_patterns(self, thread_id: UUID) -> Dict[str, Any]:
        """Analyze conversation patterns and interaction dynamics"""
        messages = []
        with self.neo4j.get_session() as session:
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                    RETURN m
                    ORDER BY m.created_at
                """,
                thread_id=str(thread_id)
                )
            )
            messages = [dict(record["m"]) for record in result]

        if not messages:
            raise ContextManagerException(f"No messages found in thread {thread_id}")

        # Analyze response times
        response_times = []
        prev_message = None
        for message in messages:
            if prev_message and prev_message["role"] != message["role"]:
                current_time = datetime.fromisoformat(str(message["created_at"]))
                prev_time = datetime.fromisoformat(str(prev_message["created_at"]))
                response_times.append((current_time - prev_time).total_seconds())
            prev_message = message

        # Analyze message lengths
        message_lengths = {
            "user": [len(m["content"]) for m in messages if m["role"] == "user"],
            "assistant": [len(m["content"]) for m in messages if m["role"] == "assistant"]
        }

        return {
            "response_time_analysis": {
                "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0
            },
            "message_length_analysis": {
                "user": {
                    "average_length": sum(message_lengths["user"]) / len(message_lengths["user"])
                        if message_lengths["user"] else 0,
                    "min_length": min(message_lengths["user"]) if message_lengths["user"] else 0,
                    "max_length": max(message_lengths["user"]) if message_lengths["user"] else 0
                },
                "assistant": {
                    "average_length": sum(message_lengths["assistant"]) / len(message_lengths["assistant"])
                        if message_lengths["assistant"] else 0,
                    "min_length": min(message_lengths["assistant"]) if message_lengths["assistant"] else 0,
                    "max_length": max(message_lengths["assistant"]) if message_lengths["assistant"] else 0
                }
            }
        }

    async def get_topic_evolution(self, thread_id: UUID) -> List[Dict[str, Any]]:
        """Analyze how topics evolve throughout the conversation"""
        with self.neo4j.get_session() as session:
            result = session.execute_read(
                lambda tx: tx.run("""
                    MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
                    RETURN m
                    ORDER BY m.created_at
                """,
                thread_id=str(thread_id)
                )
            )
            messages = [dict(record["m"]) for record in result]

        if not messages:
            raise ContextManagerException(f"No messages found in thread {thread_id}")

        # Group messages by time windows (e.g., 5-minute intervals)
        window_size = timedelta(minutes=5)
        windows = defaultdict(list)
        
        for message in messages:
            timestamp = datetime.fromisoformat(str(message["created_at"]))
            window_start = timestamp.replace(second=0, microsecond=0)
            window_start = window_start - timedelta(minutes=window_start.minute % 5)
            windows[window_start].append(message["content"])

        # Analyze topics for each window
        topic_evolution = []
        for window_start, window_messages in windows.items():
            combined_content = " ".join(window_messages)
            topics = await self.openai.extract_topics(combined_content)
            
            topic_evolution.append({
                "timestamp": window_start.isoformat(),
                "topics": topics,
                "message_count": len(window_messages)
            })

        return topic_evolution