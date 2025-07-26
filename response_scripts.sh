#!/bin/bash

# Script to handle incident responses based on alerts
# Logs all actions to /var/log/incident_response.log

# Ensure the log file exists and is writable
LOG_FILE="/var/log/incident_response.log"
touch "$LOG_FILE" 2>/dev/null || { echo "Error: Cannot create log file $LOG_FILE"; exit 1; }
chmod 644 "$LOG_FILE" 2>/dev/null

# Function to log actions with timestamp
log_action() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Check and restart Nginx if it's not running
if ! systemctl is-active nginx >/dev/null 2>&1; then
    if systemctl restart nginx >/dev/null 2>&1; then
        log_action "Restarted Nginx due to failure"
        echo "Nginx restarted successfully"
    else
        log_action "Failed to restart Nginx"
        echo "Error: Failed to restart Nginx" >&2
    fi
else
    log_action "Nginx is already running, no action taken"
fi

# Check disk usage and clear old logs if space is critically low
MOUNT_POINT="/"
DISK_USAGE=$(df -h "$MOUNT_POINT" | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ -n "$DISK_USAGE" ] && [ "$DISK_USAGE" -ge 80 ]; then
    if find /var/log -type f -mtime +7 -exec rm -f {} \; 2>/dev/null; then
        log_action "Cleared logs due to low disk space ($DISK_USAGE%)"
        echo "Old logs cleared successfully"
    else
        log_action "Failed to clear logs due to low disk space ($DISK_USAGE%)"
        echo "Error: Failed to clear logs" >&2
    fi
else
    log_action "Disk usage is $DISK_USAGE%, no log cleanup needed"
fi
