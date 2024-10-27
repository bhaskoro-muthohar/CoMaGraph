class ContextManagerException(Exception):
    """Base exception for Context Manager"""
    pass

class DatabaseConnectionError(ContextManagerException):
    """Raised when there's an issue connecting to Neo4j"""
    pass

class EmbeddingGenerationError(ContextManagerException):
    """Raised when OpenAI fails to generate embeddings"""
    pass

class ThreadNotFoundError(ContextManagerException):
    """Raised when a thread cannot be found"""
    pass

class MessageNotFoundError(ContextManagerException):
    """Raised when a message cannot be found"""
    pass