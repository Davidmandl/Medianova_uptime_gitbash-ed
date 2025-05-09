from flask import Flask, render_template
import requests
import time
from datetime import datetime, timedelta
import threading
import logging
import os
import sys
from collections import deque
import urllib3
import signal
import atexit

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('uptime_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)

# Global variables to store status
current_status = {
    'is_up': False,
    'last_check': None,
    'response_time': None,
    'error': None,
    'status_history': [],
    'timestamps': []
}

# Store last 30 status points for the graph
status_history = deque(maxlen=30)
timestamps = deque(maxlen=30)

def check_website(url):
    try:
        logging.info(f"Checking website: {url}")
        
        # Try different access methods
        methods = [
            {
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive'
                }
            },
            {
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive'
                }
            },
            {
                'headers': {
                    'User-Agent': 'curl/7.64.1',
                    'Accept': '*/*'
                }
            }
        ]
        
        last_error = None
        for method in methods:
            try:
                start_time = time.time()
                response = requests.get(
                    url, 
                    headers=method['headers'], 
                    timeout=5, 
                    verify=False,
                    allow_redirects=True
                )
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code < 400:
                    logging.info(f"Website is UP - Status Code: {response.status_code}, Response Time: {response_time:.2f}ms")
                    return True, response_time, None
                else:
                    last_error = f"Status code: {response.status_code}"
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
            except requests.exceptions.RequestException as e:
                last_error = str(e)
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                
        logging.error(f"All access methods failed. Last error: {last_error}")
        return False, None, last_error
            
    except Exception as e:
        error_msg = f"Critical error: {str(e)}"
        logging.error(error_msg)
        return False, None, error_msg

def monitor_website():
    url = "https://www.medianova.com"
    
    logging.info(f"Starting monitoring for {url}")
    
    # Perform initial check immediately
    is_up, response_time, error = check_website(url)
    current_time = datetime.now()
    status_history.append(1 if is_up else 0)
    timestamps.append(current_time.strftime('%H:%M:%S'))
    
    current_status.update({
        'is_up': is_up,
        'last_check': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'response_time': response_time,
        'error': error,
        'status_history': list(status_history),
        'timestamps': list(timestamps)
    })
    
    # Calculate time until next minute
    next_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
    time.sleep((next_minute - current_time).total_seconds())
    
    while True:
        try:
            is_up, response_time, error = check_website(url)
            current_time = datetime.now()
            
            # Update status history for the graph
            status_history.append(1 if is_up else 0)
            timestamps.append(current_time.strftime('%H:%M:%S'))
            
            current_status.update({
                'is_up': is_up,
                'last_check': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'response_time': response_time,
                'error': error,
                'status_history': list(status_history),
                'timestamps': list(timestamps)
            })
            
            # Calculate time until next minute
            next_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
            time.sleep((next_minute - current_time).total_seconds())
            
        except Exception as e:
            logging.error(f"Error in monitoring thread: {str(e)}")
            current_status.update({
                'is_up': False,
                'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': f"Monitoring error: {str(e)}"
            })
            time.sleep(60)  # Wait a minute before retrying

def cleanup():
    logging.info("Cleaning up resources...")
    logging.info("Cleanup completed")

@app.route('/')
def index():
    return render_template('index.html', status=current_status)

@app.route('/status')
def status():
    return current_status

def create_templates():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Medianova Uptime Monitor</title>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .logo {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo img {
            max-width: 300px;
            height: auto;
        }
        .status {
            font-size: 24px;
            margin: 20px 0;
            padding: 10px;
            border-radius: 4px;
        }
        .up {
            background-color: #d4edda;
            color: #155724;
        }
        .down {
            background-color: #f8d7da;
            color: #721c24;
        }
        .details {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        .refresh {
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .status-diagram {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="https://img-medianova.mncdn.com/wp-content/uploads/2023/02/medianova-logo.svg" alt="Medianova Logo">
        </div>
        <h1>Medianova Uptime Monitor</h1>
        <div class="status {% if status.is_up %}up{% else %}down{% endif %}">
            {% if status.is_up %}
                ✅ Website is UP
            {% else %}
                ❌ Website is DOWN
            {% endif %}
        </div>
        <div class="status-diagram">
            <h3>Status Timeline</h3>
            <div class="chart-container">
                <canvas id="statusChart"></canvas>
            </div>
        </div>
        <div class="details">
            <p>Last Check: {{ status.last_check }}</p>
            {% if status.response_time %}
                <p>Response Time: {{ "%.2f"|format(status.response_time) }}ms</p>
            {% endif %}
            {% if status.error %}
                <p>Error: {{ status.error }}</p>
            {% endif %}
        </div>
        <div class="refresh">
            <button onclick="location.reload()">Refresh Status</button>
        </div>
        <div class="footer">
            Made by David Mandl
        </div>
    </div>
    <script>
        // Initialize the chart
        const ctx = document.getElementById('statusChart').getContext('2d');
        const statusChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: {{ status.timestamps|tojson }},
                datasets: [{
                    label: 'Website Status',
                    data: {{ status.status_history|tojson }},
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        max: 1,
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return value === 1 ? 'UP' : 'DOWN';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.raw === 1 ? 'UP' : 'DOWN';
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000
                }
            }
        });

        // Auto refresh every minute
        setTimeout(function() {
            location.reload();
        }, 60000);
    </script>
</body>
</html>
        ''')

def main():
    try:
        print("Starting Medianova Uptime Monitor...")
        print("Creating templates...")
        create_templates()
        
        # Register cleanup handler
        atexit.register(cleanup)
        
        # Handle SIGINT and SIGTERM
        def signal_handler(signum, frame):
            print("\nShutting down gracefully...")
            cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("Starting monitoring thread...")
        monitor_thread = threading.Thread(target=monitor_website, daemon=True)
        monitor_thread.start()
        
        print("Starting web server...")
        print("Open http://localhost:5000 in your browser to view the status")
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error: {str(e)}")
        cleanup()
        raise

if __name__ == "__main__":
    main() 