from flask import Flask, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
import os

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_settings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# AI Models
class AITemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_type = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_type': self.template_type,
            'subject': self.subject,
            'content': self.content
        }

class TrainingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'response': self.response,
            'category': self.category
        }

class FallbackRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.String(200), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'condition': self.condition,
            'action': self.action,
            'priority': self.priority,
            'enabled': self.enabled
        }

class OfficeHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'timezone': self.timezone
        }

# AI Service class
class AIService:
    def __init__(self, app=None):
        self.app = app
        self.templates = {
            'confirmation': None,
            'cancellation': None,
            'inquiry': None
        }
        self.training_data = []
        self.fallback_rules = []
        self.office_hours = []
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.load_data()

    def load_data(self):
        with self.app.app_context():
            self.load_templates()
            self.load_training_data()
            self.load_fallback_rules()
            self.load_office_hours()

    def load_templates(self):
        with self.app.app_context():
            templates = AITemplate.query.all()
            for template in templates:
                self.templates[template.template_type] = template

    def load_training_data(self):
        with self.app.app_context():
            self.training_data = TrainingData.query.all()

    def load_fallback_rules(self):
        with self.app.app_context():
            self.fallback_rules = FallbackRule.query.order_by(FallbackRule.priority).all()

    def load_office_hours(self):
        with self.app.app_context():
            self.office_hours = OfficeHours.query.all()

    def get_template(self, template_type):
        with self.app.app_context():
            return self.templates.get(template_type)

    def get_training_response(self, question):
        with self.app.app_context():
            for data in self.training_data:
                if question.lower() in data.question.lower():
                    return data.response
            return None

    def should_fallback(self, confidence_score):
        with self.app.app_context():
            for rule in self.fallback_rules:
                if eval(rule.condition.replace('confidence_score', str(confidence_score))):
                    return rule.action
            return None

    def is_within_office_hours(self):
        with self.app.app_context():
            now = datetime.utcnow()
            current_time = now.time()
            current_day = now.weekday()
            
            for hours in self.office_hours:
                if hours.day_of_week == current_day:
                    if hours.start_time <= current_time <= hours.end_time:
                        return True
            return False

    def get_escalation_flow(self):
        with self.app.app_context():
            flow = []
            for rule in self.fallback_rules:
                if rule.enabled:
                    flow.append({
                        'condition': rule.condition,
                        'action': rule.action,
                        'priority': rule.priority
                    })
            return sorted(flow, key=lambda x: x['priority'])

    def create_template(self, template_type, subject, content):
        with self.app.app_context():
            template = AITemplate(
                template_type=template_type,
                subject=subject,
                content=content
            )
            db.session.add(template)
            db.session.commit()
            return template

    def create_training_data(self, question, response, category):
        with self.app.app_context():
            training = TrainingData(
                question=question,
                response=response,
                category=category
            )
            db.session.add(training)
            db.session.commit()
            return training

    def create_fallback_rule(self, condition, action, priority):
        with self.app.app_context():
            rule = FallbackRule(
                condition=condition,
                action=action,
                priority=priority
            )
            db.session.add(rule)
            db.session.commit()
            return rule

    def create_office_hours(self, day_of_week, start_time, end_time, timezone):
        with self.app.app_context():
            hours = OfficeHours(
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone
            )
            db.session.add(hours)
            db.session.commit()
            return hours

# API Routes
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/templates', methods=['GET'])
def get_templates():
    with app.app_context():
        templates = AITemplate.query.all()
        return jsonify([t.to_dict() for t in templates])

@ai_bp.route('/templates', methods=['POST'])
def create_template():
    with app.app_context():
        data = request.json
        template = service.create_template(
            template_type=data['template_type'],
            subject=data['subject'],
            content=data['content']
        )
        return jsonify(template.to_dict()), 201

@ai_bp.route('/training', methods=['GET'])
def get_training_data():
    with app.app_context():
        training = TrainingData.query.all()
        return jsonify([t.to_dict() for t in training])

@ai_bp.route('/training', methods=['POST'])
def create_training_data():
    with app.app_context():
        data = request.json
        training = service.create_training_data(
            question=data['question'],
            response=data['response'],
            category=data['category']
        )
        return jsonify(training.to_dict()), 201

@ai_bp.route('/fallback', methods=['GET'])
def get_fallback_rules():
    with app.app_context():
        rules = FallbackRule.query.all()
        return jsonify([r.to_dict() for r in rules])

@ai_bp.route('/fallback', methods=['POST'])
def create_fallback_rule():
    with app.app_context():
        data = request.json
        rule = service.create_fallback_rule(
            condition=data['condition'],
            action=data['action'],
            priority=data['priority'],
            enabled=data.get('enabled', True)
        )
        return jsonify(rule.to_dict()), 201

@ai_bp.route('/office-hours', methods=['GET'])
def get_office_hours():
    with app.app_context():
        hours = OfficeHours.query.all()
        return jsonify([h.to_dict() for h in hours])

@ai_bp.route('/office-hours', methods=['POST'])
def create_office_hours():
    with app.app_context():
        data = request.json
        hours = service.create_office_hours(
            day_of_week=data['day_of_week'],
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            timezone=data['timezone']
        )
        return jsonify(hours.to_dict()), 201

# Initialize AIService
service = None

@app.before_request
def init_service():
    global service
    if service is None:
        service = AIService(app)

# Register blueprint
app.register_blueprint(ai_bp, url_prefix='/ai')

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
