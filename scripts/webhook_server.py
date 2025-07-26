#!/usr/bin/env python3

from flask import Flask, request, jsonify
import subprocess
import json
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/webhook_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Map alert names to response actions
ALERT_ACTIONS = {
    'HighCpuUsage': 'high_cpu',
    'HighMemoryUsage': 'high_memory',
    'NginxDown': 'nginx_down',
    'LowDiskSpace': 'disk_space'
}

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        if not data or 'alerts' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
        
        responses = []
        
        for alert in data['alerts']:
            if alert.get('status') == 'firing':
                alert_name = alert.get('labels', {}).get('alertname', 'unknown')
                severity = alert.get('labels', {}).get('severity', 'warning')
                
                logger.info(f"Processing alert: {alert_name} (severity: {severity})")
                
                # Get the appropriate action
                action = ALERT_ACTIONS.get(alert_name, 'general')
                
                # Execute the response script
                script_path = '/root/sre-monitoring/scripts/incident_response.sh'
                
                try:
                    result = subprocess.run(
                        [script_path, action],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"Successfully executed response for {alert_name}")
                        responses.append({
                            'alert': alert_name,
                            'status': 'success',
                            'action': action
                        })
                    else:
                        logger.error(f"Failed to execute response: {result.stderr}")
                        responses.append({
                            'alert': alert_name,
                            'status': 'failed',
                            'error': result.stderr
                        })
                        
                except subprocess.TimeoutExpired:
                    logger.error(f"Response script timed out for {alert_name}")
                    responses.append({
                        'alert': alert_name,
                        'status': 'timeout'
                    })
                except Exception as e:
                    logger.error(f"Error executing response: {str(e)}")
                    responses.append({
                        'alert': alert_name,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return jsonify({
            'status': 'processed',
            'timestamp': datetime.now().isoformat(),
            'responses': responses
        }), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    # Create log directory if it doesn't exist
    os.makedirs('/var/log', exist_ok=True)
    
    logger.info("Starting webhook server on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
