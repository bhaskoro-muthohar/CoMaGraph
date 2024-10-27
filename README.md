# CoMaGraph (Context Manager Using Graph Storage) API
A project for managing conversational context using OpenAI's NLP capabilities and Neo4j for graph storage.

## Placeholder for Detailed Documentation
I'll outline a clean, modular project directory structure that incorporates OpenAI for NLP tasks.



```plaintext
llm_context_manager/
├── .env.example                    # Template for environment variables
├── .gitignore
├── README.md
├── docker-compose.yml              # Neo4j + API service
├── pyproject.toml                  # Project dependencies and config
├── Dockerfile
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py               # Dependency injection
│   │   ├── error_handlers.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── messages.py       # Message-related endpoints
│   │       ├── threads.py        # Thread management endpoints
│   │       └── analysis.py       # Analytics endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── constants.py
│   │   └── exceptions.py        # Custom exceptions
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── neo4j.py            # Neo4j connection management
│   │   └── queries/            # Neo4j Cypher queries
│   │       ├── __init__.py
│   │       ├── messages.py
│   │       ├── threads.py
│   │       └── analysis.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── message.py          # Pydantic models for messages
│   │   ├── thread.py          # Pydantic models for threads
│   │   └── analysis.py        # Pydantic models for analysis results
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── message_service.py  # Message handling logic
│   │   ├── thread_service.py   # Thread management logic
│   │   ├── openai_service.py   # OpenAI API integration
│   │   └── graph_service.py    # Neo4j operations
│   │
│   └── utils/
│       ├── __init__.py
│       ├── embeddings.py       # Embedding utilities
│       ├── text_processing.py  # Text processing helpers
│       └── validation.py       # Input validation helpers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures
│   ├── test_api/             # API endpoint tests
│   ├── test_services/        # Service layer tests
│   └── test_utils/          # Utility function tests
│
└── scripts/
    ├── seed_data.py         # Data seeding script
    └── setup_neo4j.py       # Neo4j setup script

```

Key Files and Their Contents:

1. `src/services/openai_service.py`:
```python
# Core functionalities using OpenAI
- Generate embeddings for messages
- Calculate similarity between messages
- Extract topics/entities
- Analyze sentiment
- Summarize conversation threads
```

2. `src/db/queries/messages.py`:
```python
# Example Neo4j queries
- Store messages with embeddings
- Retrieve context based on similarity
- Find related messages by topic
- Get conversation thread history
```

3. `src/models/message.py`:
```python
# Pydantic models for:
- Message creation
- Message responses
- Thread context
- Analysis results
```

4. `docker-compose.yml`:
```yaml
# Services:
- Neo4j database
- FastAPI application
- (Optional) Monitoring tools
```

Key Integration Points:

1. OpenAI Integration:
- Embeddings generation using text-embedding-ada-002
- Topic extraction using gpt-3.5-turbo or gpt-4
- Sentiment analysis
- Text similarity calculations

2. Neo4j Integration:
- Store messages with embeddings
- Query similar messages
- Manage conversation threads
- Track relationships between messages

3. API Endpoints Structure:
```plaintext
/messages/
  POST /               # Create new message
  GET /{message_id}    # Get message details
  GET /context/{message_id}  # Get relevant context

/threads/
  POST /               # Create new thread
  GET /{thread_id}     # Get thread details
  PUT /{thread_id}     # Update thread status

/analysis/
  GET /topics/{thread_id}    # Get thread topics
  GET /similar/{message_id}  # Find similar messages
```

## Project Specification
### LLM Conversation Context Manager

### 1. Core Components

#### A. Data Layer
- **Message Storage**
  - Properties:
    - id: UUID
    - content: Text content
    - created_at: Timestamp
    - role: "user" | "assistant"
    - embedding: OpenAI embedding vector
    - metadata: JSON (client info, source, etc.)
    - thread_id: Thread reference

- **Thread Management**
  - Properties:
    - id: UUID
    - status: "active" | "archived"
    - created_at: Timestamp
    - updated_at: Timestamp
    - metadata: Session context

- **Relationships**
  - NEXT: Message sequential relationship
  - SIMILAR_TO: Cross-reference similar messages
  - REFERENCES: Messages referencing previous context
  - CONTINUES: Thread continuation markers

#### B. API Interface (/api/v1)
- **Message Operations**
  ```plaintext
  POST   /messages         # Create message
  GET    /messages/{id}    # Retrieve message
  GET    /messages/search  # Search messages
  ```

- **Thread Operations**
  ```plaintext
  POST   /threads          # Create thread
  GET    /threads/{id}     # Get thread
  PUT    /threads/{id}     # Update thread
  GET    /threads/{id}/context  # Get thread context
  ```

- **Analysis Operations**
  ```plaintext
  GET    /analysis/similar/{id}    # Find similar messages
  GET    /analysis/topics/{id}     # Extract topics
  GET    /analysis/summary/{id}    # Thread summary
  ```

#### C. Service Layer
1. **OpenAI Integration Service**
   - Embedding generation (text-embedding-ada-002)
   - Topic extraction (gpt-3.5-turbo/gpt-4)
   - Context summarization
   - Similarity scoring

2. **Neo4j Service**
   - Graph operations
   - Context retrieval
   - Relationship management
   - Query optimization

3. **Thread Management Service**
   - Thread lifecycle
   - Context window management
   - Message sequencing
   - Thread archival

4. **Analysis Service**
   - Similarity search
   - Topic clustering
   - Pattern detection
   - Usage analytics

### 2. Implementation Phases

#### Phase 1: Foundation (2 weeks)
- Project setup and configuration
- Basic API structure
- Neo4j integration
- OpenAI service setup
- Essential data models

**Deliverables:**
- Working API with basic message storage
- Neo4j connection and basic queries
- OpenAI integration for embeddings
- Basic test suite

#### Phase 2: Core Functionality (3 weeks)
- Message threading
- Embedding generation
- Context management
- Basic similarity search
- Thread operations

**Deliverables:**
- Complete message threading system
- Working context retrieval
- Similarity search implementation
- Expanded test coverage

#### Phase 3: Advanced Features (2 weeks)
- Topic extraction
- Thread summarization
- Enhanced similarity search
- Pattern recognition
- Performance optimization

**Deliverables:**
- Topic extraction system
- Thread summaries
- Optimized similarity search
- Performance metrics

#### Phase 4: Polish & Optimization (1 week)
- Performance tuning
- Documentation
- Error handling
- Monitoring setup
- API refinement

**Deliverables:**
- API documentation
- Performance benchmarks
- Monitoring dashboard
- Production readiness

### 3. Technical Requirements

#### Infrastructure
- **API Framework**: FastAPI
- **Database**: Neo4j
- **AI Provider**: OpenAI
- **Container**: Docker + Docker Compose
- **Testing**: pytest
- **Documentation**: OpenAPI/Swagger

#### External Dependencies
- OpenAI API (embeddings + completion)
- Neo4j Database
- Redis (optional, for caching)
- Prometheus/Grafana (monitoring)

#### Performance Targets
- API Response Time: < 200ms (95th percentile)
- Similarity Search: < 500ms
- Context Retrieval: < 300ms
- Thread Creation: < 100ms

### 4. MVP Scope

Essential Features:
1. Message creation and storage
2. Basic thread management
3. Embedding generation and storage
4. Simple context retrieval
5. Basic similarity search
6. Thread summarization

### 5. Monitoring & Analytics

Key Metrics:
1. API response times
2. OpenAI API usage
3. Neo4j query performance
4. Thread statistics
5. Context window effectiveness
6. Similarity search accuracy

### 6. Testing Strategy

Test Categories:
1. Unit Tests
   - Service functions
   - Utility functions
   - Model validation

2. Integration Tests
   - API endpoints
   - Neo4j operations
   - OpenAI integration

3. Performance Tests
   - Load testing
   - Concurrency testing
   - Database performance

### 7. Future Enhancements

Potential Extensions:
1. Advanced caching strategies
2. Bulk operations support
3. Custom embedding fine-tuning
4. Advanced analytics dashboard
5. Multi-modal content support
6. Real-time collaboration features