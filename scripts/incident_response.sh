#!/bin/bash

# Log file for incident responses
LOG_FILE="/var/log/incident_response.log"
LOCK_FILE="/var/run/incident_response.lock"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Prevent multiple instances
if [ -f "$LOCK_FILE" ]; then
    log_message "ERROR: Another instance is already running"
    exit 1
fi
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# Function to restart Nginx
restart_nginx() {
    if ! systemctl is-active --quiet nginx; then
        log_message "ALERT: Nginx is down. Attempting restart..."
        systemctl restart nginx
        sleep 2
        if systemctl is-active --quiet nginx; then
            log_message "SUCCESS: Nginx restarted successfully"
        else
            log_message "FAILED: Nginx restart failed"
        fi
    fi
}

# Function to clear old logs
clear_old_logs() {
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $(NF-1)}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -ge 80 ]; then
        log_message "ALERT: Disk usage is ${DISK_USAGE}%. Clearing old logs..."
        
        # Clear logs older than 7 days
        DELETED_COUNT=$(find /var/log -type f -name "*.log" -mtime +7 -delete -print | wc -l)
        
        # Clear journal logs older than 3 days
        journalctl --vacuum-time=3d
        
        log_message "SUCCESS: Deleted $DELETED_COUNT old log files"
        
        # Check disk usage after cleanup
        NEW_DISK_USAGE=$(df -h / | awk 'NR==2 {print $(NF-1)}' | sed 's/%//')
        log_message "INFO: Disk usage after cleanup: ${NEW_DISK_USAGE}%"
    fi
}

# Function to restart high CPU processes
handle_high_cpu() {
    log_message "ALERT: High CPU usage detected"
    
    # Get top CPU consuming processes
    HIGH_CPU_PROCS=$(ps aux --sort=-%cpu | head -n 6 | tail -n 5)
    log_message "INFO: Top CPU processes:\n$HIGH_CPU_PROCS"
    
    # If stress test is running, kill it
    if pgrep stress > /dev/null; then
        log_message "WARNING: Killing stress test processes"
        pkill stress
    fi
}

# Function to handle high memory usage
handle_high_memory() {
    log_message "ALERT: High memory usage detected"
    
    # Clear system caches
    sync && echo 3 > /proc/sys/vm/drop_caches
    log_message "INFO: Cleared system caches"
    
    # Show memory stats
    FREE_MEM=$(free -h | grep Mem | awk '{print $4}')
    log_message "INFO: Free memory after cache clear: $FREE_MEM"
}

# Main execution based on alert type
ALERT_TYPE="${1:-general}"

case "$ALERT_TYPE" in
    "nginx_down")
        restart_nginx
        ;;
    "disk_space")
        clear_old_logs
        ;;
    "high_cpu")
        handle_high_cpu
        ;;
    "high_memory")
        handle_high_memory
        ;;
    *)
        log_message "INFO: Running general health checks"
        restart_nginx
        clear_old_logs
        ;;
esac

log_message "INFO: Incident response completed"
