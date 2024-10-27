from fastapi.testclient import TestClient

def test_create_message(client: TestClient):
    """Test message creation"""
    # Create a thread first
    thread_response = client.post(
        "/api/v1/threads/",
        json={"metadata": {}}
    )
    thread_id = thread_response.json()["id"]
    
    # Create message
    response = client.post(
        "/api/v1/messages/",
        json={
            "content": "Hello, world!",
            "role": "user",
            "thread_id": thread_id,
            "metadata": {"source": "test"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "Hello, world!"
    assert data["role"] == "user"