from datetime import datetime
from ai_settings import db

class AutomationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    message_id = db.Column(db.String(100), nullable=False)
    handled_by = db.Column(db.String(20), nullable=False)  # 'ai' or 'human'
    confidence_score = db.Column(db.Float)
    response_time = db.Column(db.Float)  # in seconds
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'handled_by': self.handled_by,
            'confidence_score': self.confidence_score,
            'response_time': self.response_time
        }

class MessageMatchRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_messages = db.Column(db.Integer, nullable=False)
    auto_resolved = db.Column(db.Integer, nullable=False)
    match_rate = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_messages': self.total_messages,
            'auto_resolved': self.auto_resolved,
            'match_rate': self.match_rate
        }

class FailedQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    message = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(100))  # What the AI thought the intent was
    actual_intent = db.Column(db.String(100))  # What it should have been
    confidence_score = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'intent': self.intent,
            'actual_intent': self.actual_intent,
            'confidence_score': self.confidence_score
        }

class DailyConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_conversations = db.Column(db.Integer, nullable=False)
    peak_hour = db.Column(db.Integer)  # 0-23
    average_response_time = db.Column(db.Float)  # in seconds
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_conversations': self.total_conversations,
            'peak_hour': self.peak_hour,
            'average_response_time': self.average_response_time
        }
