# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the StreamOps Reliability Platform.

## Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured to communicate with your cluster
- Docker installed for building images

## Quick Start

### 1. Build Docker Images

```bash
# Build all service images
docker build -t streamops/auth-service:latest ./services/auth_service
docker build -t streamops/catalog-service:latest ./services/catalog_service
docker build -t streamops/playback-service:latest ./services/playback_service
docker build -t streamops/recommendation-service:latest ./services/recommendation_service
docker build -t streamops/notification-service:latest ./services/notification_service
docker build -t streamops/integrity-service:latest ./services/integrity_service
docker build -t streamops/gateway:latest ./gateway
```

### 2. Load Images into Cluster (if using minikube/kind)

```bash
# For minikube
minikube image load streamops/auth-service:latest
minikube image load streamops/catalog-service:latest
minikube image load streamops/playback-service:latest
minikube image load streamops/recommendation-service:latest
minikube image load streamops/notification-service:latest
minikube image load streamops/integrity-service:latest
minikube image load streamops/gateway:latest
```

### 3. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -k .

# Or apply individual files
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
kubectl apply -f kafka.yaml
kubectl apply -f auth-service.yaml
kubectl apply -f catalog-service.yaml
kubectl apply -f playback-service.yaml
kubectl apply -f recommendation-service.yaml
kubectl apply -f notification-service.yaml
kubectl apply -f integrity-service.yaml
kubectl apply -f gateway.yaml
kubectl apply -f monitoring.yaml
```

### 4. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n streamops

# Check services
kubectl get svc -n streamops

# Check logs for a specific service
kubectl logs -n streamops deployment/auth-service
```

### 5. Access Services

```bash
# Port forward to gateway
kubectl port-forward -n streamops svc/gateway 8000:8000

# Access the API
curl http://localhost:8000/health
```

## Services

- **Gateway**: LoadBalancer on port 8000
- **Auth Service**: ClusterIP on port 8001
- **Catalog Service**: ClusterIP on port 8002
- **Playback Service**: ClusterIP on port 8003
- **Recommendation Service**: ClusterIP on port 8004
- **Notification Service**: ClusterIP on port 8005
- **Integrity Service**: ClusterIP on port 8006
- **Prometheus**: LoadBalancer on port 9090
- **Grafana**: LoadBalancer on port 3000
- **Jaeger**: LoadBalancer on port 16686

## Scaling

All services have HorizontalPodAutoscalers configured:

```bash
# Check HPA status
kubectl get hpa -n streamops

# Manual scaling
kubectl scale deployment auth-service -n streamops --replicas=5
```

## Monitoring

Access monitoring dashboards:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

## Cleanup

```bash
# Delete all resources
kubectl delete -k .

# Or delete namespace
kubectl delete namespace streamops
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n streamops
kubectl logs <pod-name> -n streamops
```

### Service connectivity issues
```bash
kubectl exec -n streamops <pod-name> -- curl http://auth-service:8001/health
```

### Persistent volume issues
```bash
kubectl get pv -n streamops
kubectl get pvc -n streamops
```
