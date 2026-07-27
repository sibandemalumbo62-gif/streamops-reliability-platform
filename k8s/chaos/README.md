# Chaos Engineering Configuration

This directory contains chaos engineering experiments for testing system resilience using Chaos Mesh.

## Prerequisites

Install Chaos Mesh in your Kubernetes cluster:

```bash
# Install Chaos Mesh
curl -sSL https://mirrors.chaos-mesh.org/v2.6.2/install.sh | bash

# Verify installation
kubectl get pods -n chaos-mesh
```

## Chaos Experiments

### Pod Kill
Randomly terminates pods to test self-healing capabilities.

**Files:**
- `pod-kill.yaml` - Pod termination experiments

### Network Delay
Introduces network latency to test system resilience to network issues.

**Files:**
- `network-delay.yaml` - Network delay experiments

### CPU Stress
Increases CPU load to test system resilience under high CPU usage.

**Files:**
- `cpu-stress.yaml` - CPU stress experiments

### Memory Stress
Increases memory usage to test system resilience under memory pressure.

**Files:**
- `memory-stress.yaml` - Memory stress experiments

### I/O Stress
Increases disk I/O to test system resilience under I/O pressure.

**Files:**
- `io-stress.yaml` - I/O stress experiments

## Usage

### Apply Chaos Experiments

```bash
# Apply all chaos experiments
kubectl apply -f k8s/chaos/

# Apply specific experiment type
kubectl apply -f k8s/chaos/pod-kill.yaml
kubectl apply -f k8s/chaos/network-delay.yaml
```

### Monitor Chaos Experiments

```bash
# List all chaos experiments
kubectl get podchaos -n streamops
kubectl get networkchaos -n streamops
kubectl get stresschaos -n streamops

# View experiment details
kubectl describe podchaos pod-kill-auth-service -n streamops

# View experiment events
kubectl get events --field-selector involvedObject.kind=PodChaos -n streamops
```

### Pause/Resume Experiments

```bash
# Pause an experiment
kubectl patch podchaos pod-kill-auth-service -n streamops -p '{"spec":{"scheduler":{"cron":"@never"}}}'

# Resume an experiment
kubectl patch podchaos pod-kill-auth-service -n streamops -p '{"spec":{"scheduler":{"cron":"@every 5m"}}}'
```

### Delete Chaos Experiments

```bash
# Delete specific experiment
kubectl delete podchaos pod-kill-auth-service -n streamops

# Delete all chaos experiments
kubectl delete -f k8s/chaos/
```

## Best Practices

1. **Start Small**: Begin with mild chaos experiments and gradually increase intensity
2. **Monitor Continuously**: Always monitor system metrics during chaos experiments
3. **Test During Off-Peak**: Run chaos experiments during low-traffic periods
4. **Have Rollback Plan**: Always be ready to quickly stop chaos experiments
5. **Document Results**: Record system behavior and recovery times
6. **Gradual Rollout**: Test chaos experiments in staging before production

## Safety Measures

- All experiments are scheduled with reasonable intervals
- Experiments target only one pod at a time (mode: one)
- Duration is limited to prevent prolonged disruption
- Critical services have Pod Disruption Budgets for protection

## Metrics to Monitor

During chaos experiments, monitor:
- Pod restart counts
- Service availability
- Response times
- Error rates
- Resource utilization
- SLO compliance

## Integration with CI/CD

Chaos experiments can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Chaos Experiments
  run: |
    kubectl apply -f k8s/chaos/
    sleep 300  # Wait for experiments to run
    kubectl delete -f k8s/chaos/
    kubectl run smoke-tests --image=smoke-test-image
```

## Troubleshooting

### Chaos Mesh not installed
```bash
kubectl get pods -n chaos-mesh
# If empty, install Chaos Mesh
```

### Experiments not running
```bash
kubectl describe podchaos <experiment-name> -n streamops
# Check for errors in events
```

### System not recovering
```bash
# Immediately delete all chaos experiments
kubectl delete -f k8s/chaos/

# Check pod status
kubectl get pods -n streamops

# Check HPA status
kubectl get hpa -n streamops
```
