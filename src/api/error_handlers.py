from fastapi import Request, status
from fastapi.responses import JSONResponse
from ..core.exceptions import (
    ContextManagerException,
    DatabaseConnectionError,
    EmbeddingGenerationError,
    ThreadNotFoundError,
    MessageNotFoundError
)

async def context_manager_exception_handler(
    request: Request,
    exc: ContextManagerException
) -> JSONResponse:
    """Handle custom exceptions"""
    error_mapping = {
        DatabaseConnectionError: {
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "message": "Database connection error"
        },
        EmbeddingGenerationError: {
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "message": "Failed to generate embeddings"
        },
        ThreadNotFoundError: {
            "status_code": status.HTTP_404_NOT_FOUND,
            "message": "Thread not found"
        },
        MessageNotFoundError: {
            "status_code": status.HTTP_404_NOT_FOUND,
            "message": "Message not found"
        }
    }
    
    error_info = error_mapping.get(
        type(exc),
        {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error"
        }
    )
    
    return JSONResponse(
        status_code=error_info["status_code"],
        content={
            "error": error_info["message"],
            "detail": str(exc)
        }
    )