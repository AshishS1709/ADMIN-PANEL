from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from models import db, Worker, StandbyRecord, Shift
from ai_settings.ai_routes import ai_bp

app = Flask(__name__)
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///standby.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Register blueprints
app.register_blueprint(ai_bp)

with app.app_context():
    db.create_all()

# Routes
@app.route('/api/workers', methods=['GET'])
def get_workers():
    workers = Worker.query.all()
    return jsonify([worker.to_dict() for worker in workers])

@app.route('/api/workers/<int:worker_id>', methods=['GET'])
def get_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    return jsonify(worker.to_dict())

@app.route('/api/standby', methods=['GET'])
def get_standby_list():
    filter_by = request.args.get('filterBy', 'date')
    value = request.args.get('value')
    
    query = StandbyRecord.query.join(Worker)
    
    if filter_by == 'date':
        if value:
            date = datetime.strptime(value, '%Y-%m-%d')
            query = query.filter(StandbyRecord.date == date)
    elif filter_by == 'location':
        if value:
            query = query.filter(Worker.location == value)
    elif filter_by == 'role':
        if value:
            query = query.filter(Worker.role == value)
    
    records = query.all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/shifts', methods=['GET'])
def get_shifts():
    shifts = Shift.query.all()
    return jsonify([shift.to_dict() for shift in shifts])

@app.route('/api/assign-shift', methods=['POST'])
def assign_shift():
    data = request.json
    record_id = data.get('recordId')
    shift_id = data.get('shiftId')
    
    record = StandbyRecord.query.get_or_404(record_id)
    shift = Shift.query.get_or_404(shift_id)
    
    # Update worker's reliability rating
    record.worker.total_shifts += 1
    record.worker.shifts_completed += 1
    record.worker.reliability_rating = record.worker.calculate_reliability()
    
    # Update shift status
    shift.status = 'filled'
    
    # Update standby record
    record.shift_assigned = True
    record.status = 'confirmed'
    record.ai_status = 'confirmed'
    record.shift_id = shift_id
    
    db.session.commit()
    
    return jsonify({
        'message': 'Shift assigned successfully',
        'record': record.to_dict(),
        'shift': shift.to_dict()
    })

@app.route('/api/notify-workers', methods=['POST'])
def notify_workers():
    data = request.json
    location = data.get('location')
    role = data.get('role')
    date = datetime.strptime(data.get('date'), '%Y-%m-%d')
    
    # Find suitable workers
    workers = Worker.query.filter_by(location=location, role=role).all()
    
    # Create standby records
    for worker in workers:
        standby_record = StandbyRecord(
            worker_id=worker.id,
            date=date,
            status='pending',
            ai_status='pending'
        )
        db.session.add(standby_record)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Workers notified successfully',
        'workers_notified': len(workers)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
