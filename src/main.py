from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes.messages import router as messages_router
from .api.routes.threads import router as threads_router
from .api.error_handlers import context_manager_exception_handler
from .core.exceptions import ContextManagerException
from .core.config import get_settings
from .db.neo4j import Neo4jService
from contextlib import asynccontextmanager

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    neo4j_service = Neo4jService()
    neo4j_service.init_constraints()
    yield
    # Shutdown
    neo4j_service.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
app.add_exception_handler(
    ContextManagerException,
    context_manager_exception_handler
)

# Register routers
app.include_router(
    messages_router,
    prefix=settings.API_V1_STR
)
app.include_router(
    threads_router,
    prefix=settings.API_V1_STR
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""    
    return {"status": "healthy"}