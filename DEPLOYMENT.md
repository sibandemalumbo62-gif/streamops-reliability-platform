# StreamOps Reliability Platform - Deployment Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Local Development with Docker Compose

1. **Clone the repository**
```bash
git clone <repository-url>
cd streamops-reliability-platform
```

2. **Start all services**
```bash
docker-compose up -d
```

This will start:
- 6 PostgreSQL databases (one for each service)
- Redis
- API Gateway (port 8000)
- Auth Service (port 8001)
- Catalog Service (port 8002)
- Playback Service (port 8003)
- Recommendation Service (port 8004)
- Notification Service (port 8005)
- Integrity Service (port 8006)

3. **Verify services are running**
```bash
docker-compose ps
```

4. **Access the API Gateway**
```
http://localhost:8000
```

### Manual Setup (Without Docker)

#### 1. Database Setup

Create databases for each service:
```sql
CREATE DATABASE auth_db;
CREATE DATABASE catalog_db;
CREATE DATABASE playback_db;
CREATE DATABASE recommendation_db;
CREATE DATABASE notification_db;
CREATE DATABASE integrity_db;
```

#### 2. Environment Configuration

Copy `.env.example` files for each service and configure:
```bash
# For each service
cp .env.example .env
# Edit .env with your configuration
```

#### 3. Install Dependencies

For each service:
```bash
cd services/<service_name>
pip install -r requirements.txt
```

#### 4. Run Database Migrations

For each service with Alembic:
```bash
alembic upgrade head
```

#### 5. Start Services

For each service:
```bash
uvicorn services.<service_name>.app.main:app --host 0.0.0.0 --port <port>
```

## Service Endpoints

### API Gateway (Port 8000)
- `GET /health` - Health check
- `GET /` - API information
- `POST /api/v1/auth/*` - Auth service routes
- `GET /api/v1/catalog/*` - Catalog service routes
- `POST /api/v1/playback/*` - Playback service routes
- `GET /api/v1/recommendations/*` - Recommendation service routes
- `POST /api/v1/notifications/*` - Notification service routes
- `POST /api/v1/events/*` - Integrity service routes

### Auth Service (Port 8001)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/password-reset/request` - Request password reset
- `POST /auth/password-reset/confirm` - Confirm password reset
- `GET /users/{user_id}` - Get user info
- `PATCH /users/{user_id}` - Update user info

### Catalog Service (Port 8002)
- `POST /catalog/` - Create content
- `GET /catalog/` - Get all content
- `GET /catalog/{content_id}` - Get specific content
- `PATCH /catalog/{content_id}` - Update content
- `DELETE /catalog/{content_id}` - Delete content
- `GET /search/` - Search content

### Playback Service (Port 8003)
- `POST /playback/start` - Start playback session
- `POST /playback/{session_id}/stream-url` - Get stream URL
- `PATCH /playback/{session_id}` - Update playback
- `POST /playback/{session_id}/pause` - Pause playback
- `POST /playback/{session_id}/resume` - Resume playback
- `POST /playback/{session_id}/stop` - Stop playback
- `GET /sessions/{session_id}` - Get session info
- `GET /sessions/user/{user_id}/active` - Get user active sessions

### Recommendation Service (Port 8004)
- `GET /recommendations/{user_id}` - Get recommendations
- `POST /recommendations/watch-history` - Add watch history
- `GET /recommendations/{user_id}/watch-history` - Get watch history
- `GET /preferences/{user_id}` - Get user preferences
- `POST /preferences/` - Create user preferences
- `PATCH /preferences/{user_id}` - Update user preferences

### Notification Service (Port 8005)
- `POST /notifications/` - Create notification
- `POST /notifications/bulk` - Create bulk notifications
- `GET /notifications/user/{user_id}` - Get user notifications
- `GET /notifications/{notification_id}` - Get specific notification
- `PATCH /notifications/{notification_id}` - Update notification
- `POST /notifications/{notification_id}/read` - Mark as read
- `POST /notifications/user/{user_id}/read-all` - Mark all as read
- `POST /templates/` - Create template
- `GET /templates/` - Get all templates
- `GET /templates/{template_id}` - Get specific template
- `PATCH /templates/{template_id}` - Update template
- `DELETE /templates/{template_id}` - Delete template

### Integrity Service (Port 8006)
- `POST /events/` - Create event
- `GET /events/` - Get all events
- `GET /events/{event_id}` - Get specific event
- `GET /events/metrics` - Get event metrics
- `GET /events/health` - Get service health
- `GET /events/filter` - Filter events
- `GET /incidents/` - Get incidents
- `POST /incidents/` - Create incident
- `PATCH /incidents/{incident_id}` - Update incident

## Testing

### Run Tests for All Services

```bash
# Auth Service
cd services/auth_service
pytest app/tests/

# Catalog Service
cd services/catalog_service
pytest app/tests/

# Playback Service
cd services/playback_service
pytest app/tests/

# Recommendation Service
cd services/recommendation_service
pytest app/tests/

# Notification Service
cd services/notification_service
pytest app/tests/
```

## Database Migrations

### Create New Migration

```bash
cd services/<service_name>
alembic revision --autogenerate -m "description"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migrations

```bash
alembic downgrade -1
```

## Monitoring

### Health Checks

Each service has a health check endpoint:
```bash
curl http://localhost:<port>/health
```

### Prometheus Metrics

The Integrity Service exposes Prometheus metrics:
```bash
curl http://localhost:8006/metrics
```

## Troubleshooting

### Service Won't Start

1. Check if the port is already in use
2. Verify database connection
3. Check environment variables
4. Review service logs

### Database Connection Issues

1. Verify PostgreSQL is running
2. Check database credentials in .env
3. Ensure database exists
4. Run migrations

### Docker Compose Issues

```bash
# View logs
docker-compose logs <service_name>

# Restart specific service
docker-compose restart <service_name>

# Rebuild service
docker-compose up -d --build <service_name>

# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Production Considerations

### Security
- Change all default passwords
- Use strong SECRET_KEY values
- Enable HTTPS
- Configure proper CORS settings
- Implement proper authentication/authorization

### Scalability
- Use connection pooling
- Implement caching with Redis
- Configure horizontal pod autoscaling
- Use load balancers

### Monitoring
- Set up centralized logging
- Configure alerting
- Monitor metrics with Prometheus/Grafana
- Implement distributed tracing

### Backup
- Regular database backups
- Backup Redis data
- Document disaster recovery procedures
