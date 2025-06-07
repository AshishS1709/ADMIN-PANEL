# Booking Platform Services

A microservices-based booking platform with multiple independent services:

## Services Overview

1. **Booking Manager**
   - Port: 8002
   - Purpose: Manage shift bookings and worker assignments
   - Features:
     - Shift management
     - Worker availability tracking
     - Manual shift overrides
     - Standby worker suggestions

2. **Cancellations Panel**
   - Port: 8003
   - Purpose: Handle shift cancellations and rebooking
   - Features:
     - Cancellation tracking
     - AI-powered reason analysis
     - Automatic reply handling
     - Blacklisting repeat cancellers
     - Quick rebooking suggestions

3. **Chat Service**
   - Port: 8001
   - Purpose: Provide real-time communication
   - Features:
     - Real-time messaging
     - Message status tracking
     - Attachment support
     - Message export

4. **Dashboard Service**
   - Port: 8004
   - Purpose: Provide analytics and monitoring
   - Features:
     - Real-time metrics
     - Historical data analysis
     - Alert system
     - Custom reporting

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/AshishS1709/ADMIN-PANEL.git
```

2. Create virtual environment and install dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Run each service:
```bash
# Booking Manager
cd booking_manager
uvicorn main:app --reload --port 8002

# Cancellations Panel
cd cancellations_panel
uvicorn main:app --reload --port 8003

# Chat Service
cd chat
uvicorn main:app --reload --port 8001

# Dashboard Service
cd dashboard
uvicorn main:app --reload --port 8004
```

## Project Structure
```
booking-platform/
├── booking_manager/
│   ├── main.py
│   ├── test_booking_manager.py
│   ├── requirements.txt
│   └── bookings.db
├── cancellations_panel/
│   ├── main.py
│   ├── test_cancellations.py
│   ├── requirements.txt
│   └── cancellations.db
├── chat/
│   ├── main.py
│   ├── test_chat.py
│   ├── requirements.txt
│   └── database.py
└── dashboard/
    ├── main.py
    ├── test_dashboard.py
    └── requirements.txt
```

## Technology Stack

- Backend: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Testing: pytest
- Validation: Pydantic
- Python 3.10+

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
