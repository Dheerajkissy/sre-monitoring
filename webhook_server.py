from flask import Flask, request
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log the webhook request
        with open('/tmp/webhook_log.txt', 'a') as f:
            f.write(f"{timestamp}: Received webhook: {json.dumps(data)}\n")
        
        if data and 'alerts' in data:
            for alert in data['alerts']:
                if alert['status'] == 'firing' and alert['labels']['alertname'] == 'HighCpuUsage':
                    with open('/tmp/webhook_log.txt', 'a') as f:
                        f.write(f"{timestamp}: Executing script for {alert['labels']['alertname']}\n")
                    
                    # Execute the response script
                    result = subprocess.run(['/root/sre-monitoring/response_scripts.sh'], 
                                          capture_output=True, text=True)
                    
                    with open('/tmp/webhook_log.txt', 'a') as f:
                        f.write(f"{timestamp}: Script output: {result.stdout}\n")
                        if result.stderr:
                            f.write(f"{timestamp}: Script error: {result.stderr}\n")
        
        return {'status': 'processed', 'timestamp': timestamp}, 200
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/webhook_log.txt', 'a') as f:
            f.write(f"{timestamp}: Error processing webhook: {str(e)}\n")
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    # Log server start
    with open('/tmp/webhook_log.txt', 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Webhook server started\n")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
