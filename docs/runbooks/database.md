# Database Runbook

## Service Overview
- **Service Name**: PostgreSQL Database
- **Purpose**: Primary data storage for all services
- **Technology**: PostgreSQL 16
- **Version**: 16.0
- **Criticality**: SEV-0 (Critical)

## Health Checks

### Manual Health Check
```bash
# Check if database is running
docker ps | grep streamops-postgres

# Check database connectivity
docker exec streamops-postgres pg_isready

# Check database size
docker exec streamops-postgres psql -U user -.d streamops -c "SELECT pg_size_pretty(pg_database_size('streamops'));"

# Check active connections
docker exec streamops-postgres psql -U user -d streamops -c "SELECT count(*) FROM pg_stat_activity;"
```

### Automated Monitoring
- **Health Check**: `pg_isready`
- **Alert Thresholds**:
  - Connection count > 80% of max (Warning)
  - Connection count > 95% of max (Critical)
  - Replication lag > 1s (Warning)
  - Replication lag > 10s (Critical)

## Common Issues

### High Connection Count

**Symptoms**:
- "Connection refused" errors
- Slow query performance
- Connection pool exhaustion

**Diagnosis**:
```bash
# Check connection count
docker exec streamops-postgres psql -U user -d streamops -c "SELECT count(*) FROM pg_stat_activity;"

# Check max connections
docker exec streamops-postgres psql -U user -d streamops -c "SHOW max_connections;"

# Check long-running queries
docker exec streamops-postgres psql -U user -d streamops -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

**Mitigation**:
1. Kill long-running queries
```bash
docker exec streamops-postgres psql -U user -d streamops -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

2. Increase max_connections in postgresql.conf
3. Implement connection pooling (PgBouncer)
4. Optimize application connection handling

**Escalation**: If connection count > 95% for > 5 minutes, escalate to SEV-0

### Slow Query Performance

**Symptoms**:
- Queries taking > 1s
- Application timeouts
- High CPU usage

**Diagnosis**:
```bash
# Enable slow query log
docker exec streamops-postgres psql -U user -d streamops -c "ALTER SYSTEM SET log_min_duration_statement = '1000';"
docker-compose restart postgres

# Check slow queries
docker logs streamops-postgres | grep "duration:"

# Analyze query performance
docker exec streamops-postgres psql -U user -d streamops -c "EXPLAIN ANALYZE SELECT * FROM events LIMIT 10;"
```

**Mitigation**:
1. Identify slow queries from logs
2. Run EXPLAIN ANALYZE on slow queries
3. Add appropriate indexes
4. Optimize query structure
5. Consider partitioning for large tables

**Escalation**: If queries consistently > 5s, escalate to SEV-1

### Disk Space Issues

**Symptoms**:
- "No space left on device" errors
- Write failures
- Database crashes

**Diagnosis**:
```bash
# Check disk usage
docker exec streamops-postgres df -h

# Check database size
docker exec streamops-postgres psql -U user -d streamops -c "SELECT pg_size_pretty(pg_database_size('streamops'));"

# Check table sizes
docker exec streamops-postgres psql -U user -d streamops -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

**Mitigation**:
1. Clean up old data
```bash
docker exec streamops-postgres psql -U user -d streamops -c "DELETE FROM events WHERE timestamp < NOW() - INTERVAL '90 days';"
```

2. VACUUM and ANALYZE
```bash
docker exec streamops-postgres psql -U user -d streamops -c "VACUUM FULL ANALYZE;"
```

3. Archive old data to cold storage
4. Add disk space
5. Implement data retention policies

**Escalation**: If disk usage > 90%, escalate to SEV-0

### Replication Lag

**Symptoms**:
- Stale data on replicas
- Inconsistent reads
- High lag metrics

**Diagnosis**:
```bash
# Check replication status
docker exec streamops-postgres psql -U user -d streamops -c "SELECT * FROM pg_stat_replication;"

# Check lag
docker exec streamops-postgres psql -U user -d streamops -c "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;"
```

**Mitigation**:
1. Check network connectivity
2. Verify replica server resources
3. Check for long-running transactions
4. Increase replication bandwidth
5. Consider synchronous replication for critical data

**Escalation**: If lag > 10s for > 5 minutes, escalate to SEV-1

## Backup and Recovery

### Backup Procedures

#### Daily Backups
```bash
# Automated daily backup at 2 AM UTC
docker exec streamops-postgres pg_dump -U user streamops > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

#### Weekly Full Backups
```bash
# Full backup with custom format
docker exec streamops-postgres pg_dump -U user -F c streamops > backup_full_$(date +%Y%m%d).dump
```

#### Point-in-Time Recovery
```bash
# Enable WAL archiving
# In postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /var/lib/postgresql/wal/%f'
```

### Recovery Procedures

#### Restore from Backup
```bash
# Stop database
docker-compose stop postgres

# Restore from backup
docker exec -i streamops-postgres psql -U user streamops < backup_20240101.sql

# Start database
docker-compose start postgres
```

#### Point-in-Time Recovery
```bash
# Restore to specific time
docker exec streamops-postgres pg_restore -U user -d streamops -t events --restore-to-time "2024-01-01 12:00:00" backup_full.dump
```

## Maintenance Procedures

### Vacuum and Analyze
```bash
# Regular vacuum
docker exec streamops-postgres psql -U user -d streamops -c "VACUUM ANALYZE;"

# Full vacuum (requires exclusive lock)
docker exec streamops-postgres psql -U user -d streamops -c "VACUUM FULL ANALYZE;"
```

### Reindex
```bash
# Reindex all tables
docker exec streamops-postgres psql -U user -d streamops -c "REINDEX DATABASE streamops;"

# Reindex specific table
docker exec streamops-postgres psql -U user -d streamops -c "REINDEX TABLE events;"
```

### Database Upgrades
```bash
# Backup before upgrade
docker exec streamops-postgres pg_dump -U user streamos > pre_upgrade_backup.sql

# Stop database
docker-compose stop postgres

# Update PostgreSQL version in docker-compose.yml

# Start new version
docker-compose up -d postgres

# Run upgrade scripts
docker exec streamops-postgres psql -U user streamops -f upgrade_script.sql
```

## Performance Tuning

### Configuration Optimization
```bash
# In postgresql.conf:
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Index Optimization
```sql
-- Create indexes on frequently queried columns
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_service ON events(service_id);
CREATE INDEX idx_events_type ON events(event_type);

-- Composite indexes for complex queries
CREATE INDEX idx_events_service_timestamp ON events(service_id, timestamp);
```

### Query Optimization
```sql
-- Use EXPLAIN ANALYZE to analyze queries
EXPLAIN ANALYZE SELECT * FROM events WHERE service_id = 'auth' AND timestamp > NOW() - INTERVAL '1 hour';

-- Add appropriate indexes based on query patterns
-- Consider partitioning for large tables
-- Use materialized views for complex aggregations
```

## Security

### Access Control
```sql
-- Create read-only user
CREATE USER readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE streamops TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- Revoke unnecessary permissions
REVOKE CREATE ON SCHEMA public FROM public;
```

### Encryption
- Enable SSL/TLS for connections
- Encrypt backups at rest
- Use pgcrypto for sensitive data
- Rotate encryption keys regularly

### Auditing
```sql
-- Enable logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;

-- Monitor for suspicious activity
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

## Escalation Contacts

### Primary
- **On-Call DBA**: dba-oncall@mediastream.com
- **Engineering Manager**: eng-manager@mediastream.com

### Secondary
- **VP Engineering**: vp-eng@mediastream.com
- **CTO**: cto@mediastream.com

## Disaster Recovery

### Complete Database Failure
1. Verify backup integrity
2. Restore from latest backup
3. Verify data consistency
4. Update application connections
5. Monitor for 24 hours

### Data Center Outage
1. Failover to replica in different region
2. Update DNS to point to new location
3. Verify all services connect
4. Monitor performance
5. Plan return to primary

### Ransomware Attack
1. Isolate affected systems
2. Preserve evidence
3. Restore from offline backups
4. Change all credentials
5. Investigate attack vector
6. Implement additional security measures
