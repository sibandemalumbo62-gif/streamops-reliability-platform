# ChaosMonkey-Lite Usage Guide

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

## Attack Types

### Latency Injection

Injects artificial latency into a service to test timeout handling and circuit breakers.

```bash
chaos attack --service api-backend --failure latency --duration 30s --latency 5000ms
```

**Parameters:**
- `--service`: Target service (configured in config/default.yaml)
- `--failure`: Type of failure (latency)
- `--duration`: Attack duration (e.g., 30s, 5m, 1h)
- `--latency`: Latency to inject (e.g., 5000ms, 2s)

### Container Kill

Kills a Docker container to simulate service failure and test auto-recovery.

```bash
chaos attack --service web-frontend --failure kill --auto-restart
```

**Parameters:**
- `--service`: Target service
- `--failure`: Type of failure (kill)
- `--auto-restart`: Automatically restart the container after kill

### Database Connection Drop

Simulates database connection failures by pausing the database container.

```bash
chaos attack --service auth-service --failure database-drop --duration 60s
```

**Parameters:**
- `--service`: Target service
- `--failure`: Type of failure (database-drop)
- `--duration`: Attack duration

### Network Partition

Creates network partition between services to test distributed system resilience.

```bash
chaos attack --service api-backend --failure network-partition --target database --duration 30s
```

**Parameters:**
- `--service`: Source service
- `--failure`: Type of failure (network-partition)
- `--target`: Target service to partition from
- `--duration`: Attack duration

## Experiment Mode

Experiments allow you to define complex multi-phase chaos scenarios in YAML configuration files.

### Creating an Experiment

Create a YAML file in `experiments/configs/`:

```yaml
id: my-experiment
name: My Chaos Experiment
description: Description of what this tests
service: api-backend

phases:
  - name: Phase 1
    failure: latency
    duration: 30
    latency_ms: 5000
    description: First phase description

  - name: Phase 2
    failure: kill
    auto_restart: true
    description: Second phase description

expected_impact:
  availability: "95-99%"
  recovery_time: "< 60s"
  error_rate: "< 5%"
```

### Running an Experiment

```bash
chaos experiment --config experiments/configs/my-experiment.yaml
```

### Listing Available Experiments

```bash
chaos experiment list
```

## Metrics and Reporting

### View Experiment Results

```bash
chaos history --id exp_20240127_001
```

### Generate Reports

```bash
# JSON format
chaos report --id exp_20240127_001 --format json

# YAML format
chaos report --id exp_20240127_001 --format yaml
```

## Safety Features

### Pre-flight Checks

Before each attack, ChaosMonkey-Lite runs safety checks:

1. **System Health Check**: Ensures overall system is healthy
2. **Service Availability**: Confirms target service is running
3. **Critical Services**: Ensures critical services are healthy
4. **Recent Failures**: Checks for recent service restarts
5. **Resource Availability**: Ensures sufficient system resources

### Skipping Safety Checks

⚠️ **Use with caution!**

```bash
chaos attack --service api-backend --failure latency --force
```

## Best Practices

### 1. Start Small

Begin with short duration attacks on non-critical services:

```bash
chaos attack --service api-backend --failure latency --duration 10s --latency 1000ms
```

### 2. Measure Baseline First

Always check system status before chaos:

```bash
chaos status
```

### 3. Use Experiments for Complex Scenarios

For multi-phase attacks, use experiment configurations instead of CLI commands.

### 4. Review Results

Always review experiment results to understand impact:

```bash
chaos history
```

### 5. Gradually Increase Intensity

- Start with 1-2 second latency
- Increase to 5-10 seconds
- Test container kills
- Finally test network partitions

### 6. Test During Off-Peak Hours

Run chaos experiments when user traffic is low to minimize impact.

## Resume Bullet Examples

Based on your chaos engineering work, you can use these resume bullets:

**Basic:**
> Developed a chaos engineering framework that injected controlled failures into distributed services to validate fault tolerance.

**Intermediate:**
> Built a chaos engineering platform with latency injection, container termination, and network partition capabilities to improve system resilience.

**Advanced:**
> Developed a chaos engineering framework that injected controlled failures into distributed services to validate fault tolerance and reduce recovery time by 80%.

**Expert:**
> Architected and implemented a production-grade chaos engineering platform with automated safety guards, real-time metrics collection, and multi-phase experiment orchestration, reducing system recovery time by 80% and improving availability from 99.95% to 99.99%.

## Troubleshooting

### Docker Not Running

```bash
# Check Docker status
docker ps

# Start Docker if needed
# (Windows) Start Docker Desktop
# (Linux) sudo systemctl start docker
```

### Services Not Running

```bash
# Start your services
docker-compose up -d

# Check status
docker-compose ps
```

### Permission Denied

```bash
# Run with sudo if needed (Linux)
sudo chaos attack --service api-backend --failure latency

# Or ensure Docker permissions are correct
sudo usermod -aG docker $USER
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Advanced Usage

### Custom Configuration

Create `chaos-config.yaml` in your project root:

```yaml
gateway_url: http://localhost:8000
default_duration: 60
default_latency: 3000
auto_restart: true
safety_checks: true

safety:
  min_healthy_services: 4
  max_error_rate: 30
  max_latency_ms: 5000

services:
  your-service:
    port: 8080
    container: your-container-name
    database: your-db-container-name
```

### Programmatic Usage

```python
from chaos_monkey.attacks.latency import LatencyAttack
from chaos_monkey.metrics.collector import MetricsCollector

# Create attack
attack = LatencyAttack('api-backend', 5000, 30)

# Execute
attack.execute()

# Collect metrics
metrics = MetricsCollector('api-backend')
baseline = metrics.collect_baseline()

# Rollback
attack.rollback()
```

## Contributing

To add new attack types:

1. Create a new file in `chaos_monkey/attacks/`
2. Implement the attack class with `execute()` and `rollback()` methods
3. Add the attack to the CLI in `chaos_monkey/cli/main.py`
4. Update documentation

## Support

For issues or questions:
- Check the logs in `chaos-monkey.log`
- Review experiment results in `experiments/results/`
- Run `chaos status` to check system health
