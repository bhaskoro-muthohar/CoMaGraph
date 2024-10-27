# CoMaGraph (Context Manager Using Graph Storage) API

## Overview

CoMaGraph is a context management system that uses graph database (Neo4j) to store conversational data and OpenAI's embeddings to enable semantic search and context retrieval. The system maintains conversation threads, analyzes message patterns, and provides insights into conversation dynamics.

## Features

- **Thread Management**
  - Create and manage conversation threads
  - Track thread status and metadata
  - Retrieve thread context

- **Message Management**
  - Store messages with OpenAI embeddings
  - Link messages to threads
  - Support for user and assistant roles

- **Semantic Search**
  - Find similar messages using embeddings
  - Context-aware message retrieval
  - Topic-based search

- **Analytics**
  - Thread statistics
  - Conversation pattern analysis
  - Topic evolution tracking

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Neo4j**: Graph database for storing conversational data
- **OpenAI**: NLP capabilities and embeddings
- **Python 3.11+**: Core programming language
- **Docker**: Container support for Neo4j

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- OpenAI API key
- Git

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/comagraph.git
cd comagraph
```

2. **Set up the environment:**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

4. **Start Neo4j:**
```bash
docker-compose up -d
```

## Running the Application

1. **Start the API server:**
```bash
uvicorn src.main:app --reload
```

2. **Access the API:**
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## API Usage

### Create a Thread
```bash
curl -X POST http://localhost:8000/api/v1/threads/ \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"source": "example"}}'
```

### Add a Message
```bash
curl -X POST http://localhost:8000/api/v1/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, world!",
    "role": "user",
    "thread_id": "",
    "metadata": {}
  }'
```

### Get Thread Analytics
```bash
curl http://localhost:8000/api/v1/analysis/thread//stats
```

## Project Structure
```
src/
├── api/               # API routes and dependencies
├── core/              # Core configurations and constants
├── db/                # Database operations
├── models/            # Pydantic models
├── services/          # Business logic
└── main.py           # Application entry point

```

## API Endpoints

### Messages
- `POST /api/v1/messages/` - Create message
- `GET /api/v1/messages/{id}` - Get message
- `GET /api/v1/messages/similar/` - Find similar messages

### Threads
- `POST /api/v1/threads/` - Create thread
- `GET /api/v1/threads/{id}` - Get thread
- `GET /api/v1/threads/{id}/context` - Get thread context

### Analysis
- `GET /api/v1/analysis/thread/{id}/stats` - Get thread statistics
- `GET /api/v1/analysis/thread/{id}/patterns` - Analyze conversation patterns
- `GET /api/v1/analysis/thread/{id}/topics` - Track topic evolution

## Docker Support

The project includes Docker support for both the API and Neo4j. To run the entire stack in containers:

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

Required environment variables in `.env`:

```plaintext
# API Settings
API_V1_STR="/api/v1"
PROJECT_NAME="CoMaGraph"

# Neo4j Settings
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your_password"

# OpenAI Settings
OPENAI_API_KEY="your-openai-api-key"

# Performance Settings
SIMILARITY_THRESHOLD=0.8
CONTEXT_WINDOW_SIZE=10
```

## Development

To set up the development environment:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest tests/
```

3. Start the development server:
```bash
uvicorn src.main:app --reload
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.