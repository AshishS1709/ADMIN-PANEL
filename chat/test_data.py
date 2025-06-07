from datetime import datetime
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.api import MessageCreate, MessageType, MessageStatus
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def create_test_messages():
    db = SessionLocal()
    
    # Create test messages
    test_messages = [
        {
            "message_type": MessageType.BOOKING,
            "status": MessageStatus.UNRESOLVED,
            "sender_type": "agent",
            "sender_id": "agent1",
            "recipient_type": "client",
            "recipient_id": "client1",
            "content": "Hello! I'd like to book a room for next weekend"
        },
        {
            "message_type": MessageType.CANCELLATION,
            "status": MessageStatus.RESOLVED,
            "sender_type": "client",
            "sender_id": "client2",
            "recipient_type": "agent",
            "recipient_id": "agent2",
            "content": "I need to cancel my upcoming booking"
        },
        {
            "message_type": MessageType.INQUIRY,
            "status": MessageStatus.ESCALATED,
            "sender_type": "client",
            "sender_id": "client3",
            "recipient_type": "agent",
            "recipient_id": "agent3",
            "content": "I have some questions about the booking process"
        }
    ]
    
    # Create messages using API
    for message_data in test_messages:
        response = client.post(
            "/chat/messages",
            json=message_data
        )
        print(f"Created message: {response.json()}")

    # Test filtering
    print("\nTesting filters:")
    
    # Filter by message type
    response = client.get(
        "/chat/messages",
        params={"message_type": "booking"}
    )
    print(f"\nBooking messages: {response.json()}")
    
    # Filter by status
    response = client.get(
        "/chat/messages",
        params={"status": "unresolved"}
    )
    print(f"\nUnresolved messages: {response.json()}")
    
    # Export messages
    print("\nExporting messages:")
    response = client.get("/chat/messages/export")
    print(response.json())
