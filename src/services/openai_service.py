from openai import OpenAI
from ..core.config import get_settings
from typing import List, Dict, Any
import numpy as np

class OpenAIService:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text"""
        response = self.client.embeddings.create(
            model=self.settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text using GPT"""
        prompt = f"""
        Extract the main topics from the following text. Return them as a comma-separated list:
        
        Text: {text}
        
        Topics:"""

        response = await self.client.chat.completions.create(
            model=self.settings.COMPLETION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        topics = response.choices[0].message.content.strip().split(",")
        return [topic.strip() for topic in topics]

    async def summarize_thread(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a summary of the conversation thread"""
        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in messages
        ])

        prompt = f"""
        Summarize the key points of this conversation thread concisely:
        
        {conversation}
        
        Summary:"""

        response = await self.client.chat.completions.create(
            model=self.settings.COMPLETION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()