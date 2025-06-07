import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from chat.database import get_db
from chat.models import Message, Attachment, MessageType, MessageStatus

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MessageCreate(BaseModel):
    message_type: MessageType
    status: MessageStatus
    sender_type: str
    sender_id: str
    recipient_type: str
    recipient_id: str
    content: str

class MessageFilter(BaseModel):
    message_type: Optional[MessageType] = None
    status: Optional[MessageStatus] = None
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class MessageResponse(BaseModel):
    id: int
    message_type: MessageType
    status: MessageStatus
    sender_type: str
    sender_id: str
    recipient_type: str
    recipient_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    attachments: List[str]

@router.post("/messages", response_model=MessageResponse)
async def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    db_message = Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    filter: MessageFilter = Depends(),
    db: Session = Depends(get_db)
):
    query = db.query(Message)
    
    # Apply filters
    if filter.message_type:
        query = query.filter(Message.message_type == filter.message_type)
    if filter.status:
        query = query.filter(Message.status == filter.status)
    if filter.sender_id:
        query = query.filter(Message.sender_id == filter.sender_id)
    if filter.recipient_id:
        query = query.filter(Message.recipient_id == filter.recipient_id)
    if filter.start_date:
        query = query.filter(Message.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(Message.created_at <= filter.end_date)
    
    messages = query.order_by(Message.created_at.desc()).all()
    return messages

@router.put("/messages/{message_id}/status", response_model=MessageResponse)
async def update_message_status(
    message_id: int,
    status: MessageStatus,
    db: Session = Depends(get_db)
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.status = status
    db.commit()
    db.refresh(message)
    return message

@router.post("/messages/{message_id}/attachments")
async def upload_attachment(
    message_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    attachment = Attachment(
        message_id=message_id,
        file_path=file.filename,
        file_type=file.content_type
    )
    
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return {"message": "Attachment uploaded successfully", "attachment_id": attachment.id}

@router.get("/messages/export")
async def export_messages(
    filter: MessageFilter = Depends(),
    db: Session = Depends(get_db)
):
    messages = await get_messages(filter, db)
    
    # Format data for export
    export_data = []
    for message in messages:
        export_data.append({
            "id": message.id,
            "message_type": message.message_type.value,
            "status": message.status.value,
            "sender": f"{message.sender_type}:{message.sender_id}",
            "recipient": f"{message.recipient_type}:{message.recipient_id}",
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "attachments": [a.file_path for a in message.attachments]
        })
    
    return {
        "messages": export_data,
        "total_count": len(messages),
        "exported_at": datetime.utcnow().isoformat()
    }
