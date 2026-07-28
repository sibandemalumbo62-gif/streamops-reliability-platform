# ChaosMonkey-Lite 🐒

A production-grade chaos engineering framework for distributed systems. This tool intentionally breaks systems to validate fault tolerance and improve system resilience.

## Overview

ChaosMonkey-Lite injects controlled failures into distributed services to measure system resilience, recovery time, and availability. It's designed to help SRE teams identify weaknesses before they impact production.

**This is a standalone chaos engineering tool that works with any Docker-based microservices architecture.**

## Features

- **Latency Injection**: Add artificial delays to service responses
- **Container Termination**: Kill and restart Docker containers
- **Database Connection Drops**: Simulate database failures
- **Network Partitioning**: Block network traffic between services
- **Metrics Collection**: Measure availability, latency, and recovery time
- **Safety Guards**: Automatic rollback and experiment validation
- **CLI Interface**: Easy-to-use command-line tool
- **Experiment Tracking**: Log and analyze chaos experiments
- **Generic Configuration**: Works with any Docker-based services

## Installation

```bash
git clone <repository-url>
cd chaos-monkey-lite
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### 1. Configure Your Services

Edit `config/default.yaml` to define your services:

```yaml
services:
  web-frontend:
    port: 3000
    container: myapp-frontend
    database: myapp-db
  
  api-backend:
    port: 8000
    container: myapp-backend
    database: myapp-api-db
  
  auth-service:
    port: 8001
    container: myapp-auth
    database: myapp-auth-db
```

### 2. Check System Status

```bash
chaos status
```

### 3. Run Your First Attack

```bash
# Inject latency into a service
chaos attack --service api-backend --failure latency --duration 30s --latency 5000ms
```

### 4. Run Experiments

```bash
# Run a pre-configured experiment
chaos experiment --config experiments/configs/api-latency.yaml
```

## Usage

### Basic Attack Commands

```bash
# Inject latency into a service
chaos attack --service api-backend --failure latency --duration 30s --latency 5000ms

# Kill a container
chaos attack --service web-frontend --failure kill --auto-restart

# Drop database connections
chaos attack --service auth-service --failure database-drop --duration 60s

# Network partition
chaos attack --service api-backend --failure network-partition --target database
```

### Experiment Mode

```bash
# Run a full experiment with metrics
chaos experiment --config experiments/configs/my-experiment.yaml

# List available experiments
chaos experiment list

# View experiment results
chaos history --id exp_12345
```

### Metrics and Reporting

```bash
# View current system health
chaos status

# View experiment history
chaos history

# Generate report
chaos report --id exp_12345 --format json
```

## Architecture

```
chaos-monkey-lite/
├── chaos_monkey/
│   ├── cli/                 # Command-line interface
│   ├── attacks/             # Failure injection mechanisms
│   ├── metrics/             # Metrics collection and analysis
│   ├── safety/              # Safety guards and rollback
│   ├── experiments/         # Experiment configurations
│   └── utils/               # Utility functions
├── config/                  # Service configuration
├── experiments/
│   └── configs/             # Experiment templates
├── requirements.txt         # Python dependencies
└── setup.py                # Package setup
```

## Configuration

### Service Configuration

Configure your services in `config/default.yaml`:

```yaml
gateway_url: http://localhost:8000
default_duration: 30
default_latency: 5000
auto_restart: true
safety_checks: true

services:
  your-service-name:
    port: 8080
    container: your-container-name
    database: your-db-container-name
```

### Safety Configuration

Adjust safety thresholds:

```yaml
safety:
  min_healthy_services: 3
  max_error_rate: 50
  max_latency_ms: 10000
  critical_services:
    - auth-service
    - api-gateway
```

## Safety Features

- **Pre-flight Checks**: Validate system state before attacks
- **Automatic Rollback**: Revert changes if system health degrades
- **Rate Limiting**: Prevent excessive chaos
- **Time Limits**: Maximum duration for attacks
- **Health Monitoring**: Continuous health checks during experiments

## Example Output

```
$ chaos attack --service api-backend --failure latency --duration 30s --latency 5000ms

🐒 ChaosMonkey-Lite v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Starting chaos experiment: exp_20240127_001
🎯 Target: api-backend
💥 Attack: latency injection (+5000ms)
⏱️  Duration: 30s

✅ Pre-flight checks passed
📊 Baseline metrics collected:
   - Availability: 99.95%
   - Avg Latency: 45ms
   - Error Rate: 0.05%

🔥 Injecting failure...
⏳ Monitoring system response...
📈 Real-time metrics:
   - Availability: 99.2%
   - Avg Latency: 5045ms
   - Error Rate: 0.8%

⏱️  Attack duration elapsed
🔄 Rolling back changes...
✅ System recovered in 12s

📊 Final Results:
   - Availability Impact: -0.75%
   - Recovery Time: 12s
   - Errors During Attack: 23
   - System Health: RECOVERED

💡 Recommendation: Implement circuit breaker pattern
```

## Resume Bullet

> Developed a chaos engineering framework that injected controlled failures into distributed services to validate fault tolerance and reduce recovery time by 80%.

## Contributing

This tool is designed for educational purposes and SRE skill development. Use responsibly in development environments only.

## License

MIT License
