# SRE Monitoring System - Deployment Guide

## Quick Start
1. Start Prometheus: `sudo systemctl start prometheus`
2. Start Alertmanager: `sudo systemctl start alertmanager`  
3. Start Webhook Server: `python3 webhook_server.py`
4. Verify all services are running

## Service Status Check
```bash
sudo systemctl status prometheus
sudo systemctl status alertmanager
ps aux | grep webhook_server

## 3. **Add .gitignore for cleaner repo:**
```bash
cat > .gitignore << 'EOF'
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.pytest_cache/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary files
*.tmp
*.bak
*~
