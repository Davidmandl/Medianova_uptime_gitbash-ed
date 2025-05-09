import requests
import time
import logging
from datetime import datetime
import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///status.db')
db = SQLAlchemy(app)

# Database model
class StatusCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_up = db.Column(db.Boolean, nullable=False)
    response_time = db.Column(db.Float)
    status_code = db.Column(db.Integer)
    error_message = db.Column(db.String)

# Initialize database
with app.app_context():
    db.create_all()
    logger.info("Database initialized")

# Constants
TARGET_URL = "https://www.medianova.com"
CHECK_INTERVAL = 60  # seconds

def check_uptime():
    try:
        start_time = time.time()
        response = requests.get(TARGET_URL, timeout=10)
        response_time = time.time() - start_time
        
        status = StatusCheck(
            is_up=response.status_code == 200,
            response_time=response_time,
            status_code=response.status_code
        )
        
        if response.status_code == 200:
            logger.info(f"Site is UP - Response time: {response_time:.2f}s - Status code: {response.status_code}")
        else:
            logger.error(f"Site is DOWN - Status code: {response.status_code}")
            status.error_message = f"Status code: {response.status_code}"
            
        db.session.add(status)
        db.session.commit()
        return status.is_up
    except requests.RequestException as e:
        logger.error(f"Site is DOWN - Error: {str(e)}")
        status = StatusCheck(
            is_up=False,
            error_message=str(e)
        )
        db.session.add(status)
        db.session.commit()
        return False

def monitoring_thread():
    while True:
        check_uptime()
        time.sleep(CHECK_INTERVAL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    latest = StatusCheck.query.order_by(StatusCheck.timestamp.desc()).first()
    if not latest:
        return jsonify({
            'status': 'unknown',
            'last_check': None,
            'response_time': None
        })
    
    return jsonify({
        'status': 'up' if latest.is_up else 'down',
        'last_check': latest.timestamp.isoformat(),
        'response_time': latest.response_time,
        'status_code': latest.status_code,
        'error_message': latest.error_message
    })

@app.route('/api/history')
def get_history():
    checks = StatusCheck.query.order_by(StatusCheck.timestamp.desc()).limit(100).all()
    return jsonify([{
        'timestamp': check.timestamp.isoformat(),
        'is_up': check.is_up,
        'response_time': check.response_time,
        'status_code': check.status_code,
        'error_message': check.error_message
    } for check in checks])

def main():
    # Start monitoring in a separate thread
    monitor = threading.Thread(target=monitoring_thread, daemon=True)
    monitor.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main() 