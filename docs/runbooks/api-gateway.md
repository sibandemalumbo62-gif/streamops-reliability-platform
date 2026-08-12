# API Gateway Runbook

## Service Overview
- **Service Name**: API Gateway
- **Purpose**: Routes requests to microservices, handles authentication, rate limiting
- **Technology**: FastAPI, Nginx
- **Dependencies**: Auth Service, Redis, PostgreSQL
- **Criticality**: SEV-1 (High)

## Health Checks

### Manual Health Check
```bash
# Check service health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics

# Check logs
docker logs streamops-backend
```

### Automated Monitoring
- **Health Endpoint**: `/health`
- **Metrics Endpoint**: `/metrics`
- **Alert Thresholds**: 
  - Response time > 500ms (Warning)
  - Response time > 1s (Critical)
  - Error rate > 1% (Warning)
  - Error rate > 5% (Critical)

## Common Issues

### High Response Times

**Symptoms**:
- API requests taking > 500ms
- Dashboard showing increased latency
- User complaints about slowness

**Diagnosis**:
```bash
# Check current response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/

# Check database connection pool
docker exec streamops-postgres psql -U user -d streamops -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis connection
docker exec redis redis-cli ping
```

**Mitigation**:
1. Check database performance
2. Verify Redis connectivity
3. Check for memory issues
4. Review recent code changes
5. Scale horizontally if needed

**Escalation**: If response time > 2s for > 5 minutes, escalate to SEV-1

### High Error Rate

**Symptoms**:
- 5xx errors increasing
- Failed API calls
- Error logs increasing

**Diagnosis**:
```bash
# Check error logs
docker logs streamops-backend --tail 100 | grep ERROR

# Check database connectivity
docker exec streamops-postgres pg_isready

# Check service dependencies
curl http://localhost:8001/health  # Auth service
```

**Mitigation**:
1. Identify error patterns from logs
2. Check dependent services
3. Verify database connectivity
4. Check for configuration changes
5. Roll back recent deployments if needed

**Escalation**: If error rate > 10% for > 5 minutes, escalate to SEV-1

### Service Unavailable

**Symptoms**:
- 502/503 errors
- Service not responding
- Health check failing

**Diagnosis**:
```bash
# Check if service is running
docker ps | grep streamops-backend

# Check service logs
docker logs streamops-backend

# Check port availability
netstat -tlnp | grep 8000
```

**Mitigation**:
1. Restart the service
```bash
docker-compose restart backend
```

2. If restart fails, check for resource issues
```bash
docker stats streamops-backend
```

3. Check for database connectivity
```bash
docker exec streamops-postgres pg_isready
```

4. If database is down, restart database first
```bash
docker-compose restart postgres
```

**Escalation**: If service unavailable for > 5 minutes, escalate to SEV-1

### Memory Issues

**Symptoms**:
- OOM errors in logs
- Service crashes
- High memory usage

**Diagnosis**:
```bash
# Check memory usage
docker stats streamops-backend

# Check for memory leaks in logs
docker logs streamops-backend | grep -i memory
```

**Mitigation**:
1. Increase memory limits in docker-compose.yml
2. Restart service
3. Investigate for memory leaks
4. Scale horizontally

**Escalation**: If OOM errors persist, escalate to SEV-2

## Maintenance Procedures

### Rolling Deployment
```bash
# Pull latest changes
git pull

# Build new image
docker-compose build backend

# Deploy with zero downtime
docker-compose up -d --no-deps backend
```

### Database Migrations
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Verify migration
docker-compose exec backend alembic current
```

### Configuration Updates
```bash
# Update environment variables
# Edit docker-compose.yml or .env file

# Restart service
docker-compose restart backend

# Verify configuration
docker-compose exec backend env
```

## Performance Tuning

### Database Connection Pool
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### Caching Strategy
- Enable Redis caching for frequent queries
- Cache TTL: 5 minutes for user data, 1 hour for static content
- Cache invalidation on data updates

### Rate Limiting
- Default: 100 requests per minute per IP
- Authenticated users: 1000 requests per minute
- Admin users: No rate limit

## Dependencies

### Auth Service
- **Health Check**: `http://localhost:8001/health`
- **Fallback**: If unavailable, return 503
- **Retry Logic**: 3 retries with exponential backoff

### Redis
- **Purpose**: Caching, session storage
- **Health Check**: `docker exec redis redis-cli ping`
- **Fallback**: If unavailable, disable caching

### PostgreSQL
- **Purpose**: Data persistence
- **Health Check**: `docker exec streamops-postgres pg_isready`
- **Fallback**: If unavailable, return 503

## Escalation Contacts

### Primary
- **On-Call Engineer**: pagerduty@mediastream.com
- **Engineering Manager**: eng-manager@mediastream.com

### Secondary
- **Tech Lead**: tech-lead@mediastream.com
- **VP Engineering**: vp-eng@mediastream.com

## Recovery Procedures

### Complete Service Failure
1. Check infrastructure health
2. Verify database and Redis are running
3. Restart API Gateway
4. Verify health checks pass
5. Monitor for 30 minutes

### Data Corruption
1. Stop all writes to database
2. Restore from latest backup
3. Verify data integrity
4. Resume normal operations
5. Investigate root cause

### Security Incident
1. Isolate affected systems
2. Preserve logs and evidence
3. Notify security team
4. Follow security incident response
5. Communicate with stakeholders

## Documentation Updates

After any incident, update this runbook with:
- New symptoms observed
- Additional diagnostic steps
- Improved mitigation procedures
- Lessons learned
