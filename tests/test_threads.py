import pytest
from fastapi.testclient import TestClient
from uuid import UUID

def test_create_thread(client: TestClient):
    """Test thread creation"""
    response = client.post(
        "/api/v1/threads/",
        json={"metadata": {"source": "test"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert UUID(data["id"])  # Verify it's a valid UUID
    assert data["status"] == "active"

def test_thread_context(client: TestClient):
    """Test getting thread context"""
    # First create a thread
    thread_response = client.post(
        "/api/v1/threads/",
        json={"metadata": {}}
    )
    thread_id = thread_response.json()["id"]
    
    # Create a message in the thread
    message_response = client.post(
        "/api/v1/messages/",
        json={
            "content": "Test message",
            "role": "user",
            "thread_id": thread_id,
            "metadata": {}
        }
    )
    assert message_response.status_code == 200
    
    # Get thread context
    context_response = client.get(f"/api/v1/threads/{thread_id}/context")
    assert context_response.status_code == 200
    messages = context_response.json()
    assert len(messages) > 0