from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from enum import Enum
from database import engine, get_db, Base, SessionLocal

app = FastAPI(title="Booking System Dashboard API")

# Create all tables
Base.metadata.create_all(bind=engine)

class BookingStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    standby = "standby"
    pending = "pending"
    completed = "completed"

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float)  # in seconds
    agent_id = Column(String)
    customer_id = Column(String)
    service_type = Column(String)
    amount = Column(Float)

class AgentActivity(Base):
    __tablename__ = "agent_activity"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String)
    activity_type = Column(String)  # login, logout, message, booking, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration = Column(Float)  # in seconds

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # error, warning, info
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(Integer)  # 1-5, 5 being most severe
    resolved = Column(Boolean, default=False)

from chat.models import Message, Attachment

# Create all tables including chat tables
Base.metadata.create_all(bind=engine)

class DashboardStats(BaseModel):
    today_bookings: int
    today_cancellations: int
    standby_requests: int
    pending_inquiries: int
    avg_response_time: float
    total_bookings_last_7_days: Dict[str, int]
    revenue_today: float
    top_agents: List[Dict[str, Any]]
    agent_activity: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]

@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        one_week_ago = today - timedelta(days=7)
        
        # Get today's bookings
        today_bookings = db.query(Booking).filter(
            Booking.status == BookingStatus.confirmed,
            Booking.created_at >= today
        ).count()
        
        # Get today's cancellations
        today_cancellations = db.query(Booking).filter(
            Booking.status == BookingStatus.cancelled,
            Booking.created_at >= today
        ).count()
        
        # Get standby requests
        standby_requests = db.query(Booking).filter(
            Booking.status == BookingStatus.standby
        ).count()
        
        # Get pending inquiries
        pending_inquiries = db.query(Booking).filter(
            Booking.status == BookingStatus.pending
        ).count()
        
        # Calculate average response time
        avg_response_time = db.query(func.avg(Booking.response_time)).filter(
            Booking.created_at >= today
        ).scalar() or 0
        
        # Get bookings per day for last 7 days
        bookings_last_7_days = {}
        for i in range(7):
            date = today - timedelta(days=i)
            bookings = db.query(Booking).filter(
                Booking.created_at >= date,
                Booking.created_at < date + timedelta(days=1)
            ).count()
            bookings_last_7_days[date.strftime("%Y-%m-%d")] = bookings
        
        # Get today's revenue
        revenue_today = db.query(func.sum(Booking.amount)).filter(
            Booking.status == BookingStatus.confirmed,
            Booking.created_at >= today
        ).scalar() or 0
        
        # Get top performing agents
        top_agents = db.query(
            Booking.agent_id,
            func.count(Booking.id).label('booking_count'),
            func.avg(Booking.response_time).label('avg_response_time')
        ).filter(
            Booking.created_at >= today
        ).group_by(
            Booking.agent_id
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(5).all()
        
        # Get agent activity
        agent_activity = db.query(AgentActivity).order_by(
            AgentActivity.timestamp.desc()
        ).limit(10).all()
        
        # Get alerts
        alerts = db.query(Alert).filter(
            Alert.resolved == False
        ).order_by(
            Alert.severity.desc(),
            Alert.timestamp.desc()
        ).limit(5).all()
        
        # Get failed replies and unrecognized messages
        failed_replies = db.query(Alert).filter(
            Alert.type == "error",
            Alert.message.like("%reply failed%")
        ).count()
        
        unrecognized_messages = db.query(Alert).filter(
            Alert.type == "warning",
            Alert.message.like("%unrecognized message%")
        ).count()
        
        return {
            "today_bookings": today_bookings,
            "today_cancellations": today_cancellations,
            "standby_requests": standby_requests,
            "pending_inquiries": pending_inquiries,
            "avg_response_time": avg_response_time,
            "total_bookings_last_7_days": bookings_last_7_days,
            "revenue_today": revenue_today,
            "top_agents": [{"agent_id": a[0], "booking_count": a[1], "avg_response_time": a[2]} for a in top_agents],
            "agent_activity": [activity.__dict__ for activity in agent_activity],
            "alerts": [alert.__dict__ for alert in alerts]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        db.close()

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        alert.resolved = True
        db.commit()
        return {"message": "Alert resolved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        db.close()

def populate_test_data():
    db = SessionLocal()
    try:
        # Create some test bookings
        test_bookings = [
            Booking(
                status="confirmed",
                response_time=120.5,
                agent_id="agent1",
                customer_id="cust1",
                service_type="hotel",
                amount=1500.0
            ),
            Booking(
                status="cancelled",
                response_time=90.2,
                agent_id="agent2",
                customer_id="cust2",
                service_type="flight",
                amount=2500.0
            ),
            Booking(
                status="standby",
                response_time=150.3,
                agent_id="agent1",
                customer_id="cust3",
                service_type="hotel",
                amount=1200.0
            ),
            Booking(
                status="pending",
                response_time=60.1,
                agent_id="agent3",
                customer_id="cust4",
                service_type="car",
                amount=500.0
            )
        ]
        
        # Create some agent activity
        test_activities = [
            AgentActivity(
                agent_id="agent1",
                activity_type="login",
                duration=300.0
            ),
            AgentActivity(
                agent_id="agent2",
                activity_type="message",
                duration=60.0
            ),
            AgentActivity(
                agent_id="agent3",
                activity_type="booking",
                duration=120.0
            )
        ]
        
        # Create some alerts
        test_alerts = [
            Alert(
                type="error",
                message="Failed to send reply to customer 123",
                severity=4
            ),
            Alert(
                type="warning",
                message="Unrecognized message from customer 456",
                severity=3
            )
        ]
        
        # Add to database
        db.add_all(test_bookings)
        db.add_all(test_activities)
        db.add_all(test_alerts)
        db.commit()
        
        print("Test data populated successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    
    # Populate test data
    populate_test_data()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
