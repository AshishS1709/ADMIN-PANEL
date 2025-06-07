import os
import sys
import json
import requests
import time

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chat_service():
    print("Testing chat service...")
    print("\nWaiting for server to start...")
    time.sleep(2)
    
    try:
        # Create test message
        print("\nCreating test message...")
        message_data = {
            "message_type": "booking",
            "status": "unresolved",
            "sender_type": "agent",
            "sender_id": "agent1",
            "recipient_type": "client",
            "recipient_id": "client1",
            "content": "Hello! I'd like to book a room for next weekend"
        }
        
        # Create message
        response = requests.post(
            "http://localhost:8001/api/messages",
            json=message_data
        )
        if response.status_code == 200:
            print(f"\nSuccessfully created message:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nFailed to create message. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Get messages
        print("\nGetting booking messages...")
        response = requests.get(
            "http://localhost:8001/api/messages",
            params={"message_type": "booking"}
        )
        if response.status_code == 200:
            print("\nFound booking messages:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nFailed to get messages. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Update message status
        print("\nUpdating message status...")
        message_id = response.json()[0]["id"]
        response = requests.put(
            f"http://localhost:8001/api/messages/{message_id}/status",
            json={"status": "resolved"}
        )
        if response.status_code == 200:
            print("\nMessage status updated successfully:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nFailed to update message status. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Export messages
        print("\nExporting messages...")
        response = requests.get("http://localhost:8001/api/messages/export")
        if response.status_code == 200:
            print("\nSuccessfully exported messages:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nFailed to export messages. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print(f"Response status code: {response.status_code if 'response' in locals() else 'N/A'}")
        print(f"Response content: {response.text if 'response' in locals() else 'N/A'}")

if __name__ == "__main__":
    test_chat_service()
