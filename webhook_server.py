with open('/tmp/webhook_start.txt', 'a') as f:
    f.write("Server started at {}\n".format(os.times()))from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'alerts' in data:
        with open('/tmp/webhook_log.txt', 'a') as f:
            f.write(f"Received: {data}\n")
        for alert in data['alerts']:
            if alert['status'] == 'firing':
                if alert['labels']['alertname'] == 'HighCpuUsage':
                    with open('/tmp/webhook_log.txt', 'a') as f:
                        f.write(f"Executing script for {alert['labels']['alertname']}\n")
                    result = subprocess.run(['/root/sre-monitoring/response_scripts.sh'], capture_output=True, text=True)
                    with open('/tmp/webhook_log.txt', 'a') as f:
                        f.write(f"Script output: {result.stdout}\nError: {result.stderr}\n")
    else:
        with open('/tmp/webhook_log.txt', 'a') as f:
            f.write("No valid data received\n")
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
