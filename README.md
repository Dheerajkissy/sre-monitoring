# SRE Monitoring Project

## Week 1:Getting started
- Installed Kali linux

## Week 2: Monitoring Setup
- Installed Prometheus and Node Exporter for metrics collection.
- Installed Grafana for visualization with a Node Exporter dashboard.
- 
## Week 3: Alerting Setup
- Defined alerting rules for high CPU (>80%) and low disk space (<20%) in Prometheus
- Installed and configured Alertmanager for alert notifications
- Integrated Prometheus with Alertmanager for complete alerting pipeline
- Tested alerts using stress testing tools

### Services Running:
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093  
- Grafana: http://localhost:3000
- Node Exporter: localhost:9100

## Final Project Status ✅

### Completed Components:
- ✅ Prometheus monitoring setup
- ✅ Alertmanager configuration  
- ✅ Webhook server (port 5002)
- ✅ Automated incident response scripts
- ✅ 4-week testing cycle completed
- ✅ End-to-end system validation

### System Architecture:
- **Monitoring**: Prometheus + Node Exporter
- **Alerting**: Alertmanager with webhook integration
- **Response**: Automated incident response via webhook_server.py
- **Testing**: Complete 4-week validation cycle

### Deployment Status:
System is fully operational and production-ready.
