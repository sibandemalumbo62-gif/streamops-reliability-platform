# MediaStream Platform - Quick Start Guide

## Complete System Setup

This guide will help you get the entire MediaStream Platform running.

## Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Python 3.11+ (for backend development)

## Step 1: Start the Backend

The backend is a FastAPI application with PostgreSQL database.

```bash
# Start the backend with Docker Compose
docker-compose up -d

# Check if services are running
docker-compose ps
```

The backend will be available at `http://localhost:8000`

### Backend Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /services` - List services
- `GET /events` - List events
- And more...

## Step 2: Setup the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Step 3: Access the Application

1. Open your browser to `http://localhost:5173`
2. You'll be redirected to the login page
3. Enter any email and password (demo mode)
4. You'll be redirected to the dashboard

## Features

### Dashboard
- Real-time system health monitoring
- Service status indicators
- Uptime tracking
- Auto-refresh every 30 seconds

### Media Library
- Browse available content
- Search functionality
- Content cards with metadata

### Navigation
- Easy navigation between pages
- Logout functionality
- Responsive design

## Monitoring

### Prometheus Metrics
Access Prometheus metrics at `http://localhost:8000/metrics`

### Grafana Dashboard
If you have Grafana configured, import the metrics from the backend.

## Troubleshooting

### Backend not starting
```bash
# Check Docker logs
docker-compose logs backend

# Restart services
docker-compose restart
```

### Frontend not connecting to backend
- Ensure backend is running on port 8000
- Check the `.env` file in frontend directory has correct API URL
- Check browser console for errors

### Database connection issues
```bash
# Check PostgreSQL container
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

## Development

### Backend Development
```bash
# Backend is mounted as a volume, so changes are reflected immediately
# The backend auto-reloads on file changes
```

### Frontend Development
```bash
# Frontend has hot module replacement (HMR)
# Changes are reflected immediately in the browser
```

## Production Deployment

For production deployment, refer to:
- `k8s/` - Kubernetes manifests
- `infrastructure/terraform/` - AWS infrastructure
- `.github/workflows/` - CI/CD pipelines

## Support

For issues or questions, check the main README.md file.
