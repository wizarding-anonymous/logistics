from fastapi.testclient import TestClient
from chat.models import ChatThread

def test_get_chat_history(client: TestClient, test_chat_thread: ChatThread):
    """
    Test that a user can retrieve the message history for a given topic.
    """
    topic = test_chat_thread.topic
    response = client.get(f"/history/{topic}")

    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == topic
    assert len(data["messages"]) == 2
    assert data["messages"][0]["content"] == "Hello"
    assert data["messages"][1]["content"] == "Hi there"
