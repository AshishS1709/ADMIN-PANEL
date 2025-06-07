from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum

Base = declarative_base()

class MessageType(str, Enum):
    BOOKING = "booking"
    CANCELLATION = "cancellation"
    STANDBY = "standby"
    INQUIRY = "inquiry"

class MessageStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    ESCALATED = "escalated"

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_type = Column(String)
    status = Column(String)
    sender_type = Column(String)  # 'agent' or 'client'
    sender_id = Column(String)
    recipient_type = Column(String)  # 'agent' or 'client'
    recipient_id = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attachments = relationship("Attachment", back_populates="message")
    
    def __repr__(self):
        return f"Message(id={self.id}, type={self.message_type}, status={self.status})"

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    file_path = Column(String)
    file_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="attachments")
    
    def __repr__(self):
        return f"Attachment(id={self.id}, type={self.file_type})"
