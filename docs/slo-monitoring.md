# SLO Monitoring and Alerting

## Service Level Objectives (SLOs)

### API Availability
- **Target**: 99.9% monthly
- **Error Budget**: 43.2 minutes/month
- **Measurement**: Successful HTTP requests / Total HTTP requests
- **Alerting**: 
  - Warning at 99.5% (error budget at 50%消耗)
  - Critical at 99.0% (error budget exhausted)

### Response Time (p95)
- **Target**: <200ms
- **Measurement**: 95th percentile of response times
- **Alerting**:
  - Warning at 300ms
  - Critical at 500ms

### Error Rate
- **Target**: <0.1%
- **Measurement**: HTTP 5xx errors / Total requests
- **Alerting**:
  - Warning at 0.5%
  - Critical at 1.0%

### Throughput
- **Target**: >10,000 requests/minute
- **Measurement**: Requests per minute
- **Alerting**:
  - Warning at 8,000 req/min
  - Critical at 5,000 req/min

## SLI Definitions

### Availability SLI
```promql
# Successful requests ratio
sum(rate(http_requests_total{status=~"2.."}[5m])) 
/ 
sum(rate(http_requests_total[5m]))
```

### Latency SLI
```promql
# p95 latency
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

### Error Rate SLI
```promql
# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m]))
```

### Throughput SLI
```promql
# Requests per minute
sum(rate(http_requests_total[1m]))
```

## Alert Rules

### Critical Alerts (PagerDuty)
```yaml
groups:
  - name: critical_alerts
    rules:
      # Availability below 99%
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m])) 
            / 
            sum(rate(http_requests_total[5m]))
          ) > 0.01
        for: 5m
        labels:
          severity: critical
          service: api-gateway
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes"

      # p95 latency above 500ms
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, 
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.5
        for: 5m
        labels:
          severity: critical
          service: api-gateway
        annotations:
          summary: "High latency detected"
          description: "p95 latency is {{ $value }}s for the last 5 minutes"

      # Service down
      - alert: ServiceDown
        expr: up{job="api-gateway"} == 0
        for: 1m
        labels:
          severity: critical
          service: api-gateway
        annotations:
          summary: "Service is down"
          description: "API Gateway has been down for more than 1 minute"
```

### Warning Alerts (Slack)
```yaml
groups:
  - name: warning_alerts
    rules:
      # Availability below 99.5%
      - alert: ElevatedErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m])) 
            / 
            sum(rate(http_requests_total[5m]))
          ) > 0.005
        for: 10m
        labels:
          severity: warning
          service: api-gateway
        annotations:
          summary: "Elevated error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for the last 10 minutes"

      # p95 latency above 300ms
      - alert: ElevatedLatency
        expr: |
          histogram_quantile(0.95, 
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.3
        for: 10m
        labels:
          severity: warning
          service: api-gateway
        annotations:
          summary: "Elevated latency detected"
          description: "p95 latency is {{ $value }}s for the last 10 minutes"

      # Low throughput
      - alert: LowThroughput
        expr: sum(rate(http_requests_total[1m])) < 8000
        for: 5m
        labels:
          severity: warning
          service: api-gateway
        annotations:
          summary: "Low throughput detected"
          description: "Throughput is {{ $value }} requests/minute"
```

## Error Budget Calculation

### Monthly Error Budget
```python
# 99.9% availability = 0.1% downtime allowed
# 30 days = 43,200 minutes
# Error budget = 43,200 * 0.001 = 43.2 minutes

def calculate_error_budget(availability_target, period_days=30):
    total_minutes = period_days * 24 * 60
    allowed_downtime_percentage = (100 - availability_target) / 100
    error_budget_minutes = total_minutes * allowed_downtime_percentage
    return error_budget_minutes

# Example
error_budget = calculate_error_budget(99.9)  # 43.2 minutes
```

### Error Budget Burn Rate
```promql
# Current error rate vs expected error rate
(
  sum(rate(http_requests_total{status=~"5.."}[1h])) 
  / 
  sum(rate(http_requests_total[1h]))
) 
/ 
0.001  # 0.1% target error rate
```

### Error Budget Remaining
```python
def calculate_remaining_budget(incidents, error_budget_minutes):
    total_downtime = sum(incident['duration_minutes'] for incident in incidents)
    remaining = error_budget_minutes - total_downtime
    percentage_remaining = (remaining / error_budget_minutes) * 100
    return remaining, percentage_remaining
```

## SLO Dashboard (Grafana)

### Dashboard Panels

#### 1. Availability Overview
- **Panel**: Gauge chart
- **Query**: Current availability percentage
- **Thresholds**: 
  - Green: >99.9%
  - Yellow: 99.5-99.9%
  - Red: <99.5%

#### 2. Error Rate Over Time
- **Panel**: Time series graph
- **Query**: Error rate over last 24 hours
- **Threshold line**: 0.1% target

#### 3. Latency Distribution
- **Panel**: Heatmap
- **Query**: Request duration distribution
- **Threshold lines**: 200ms (p95 target)

#### 4. Error Budget Status
- **Panel**: Stat panel
- **Query**: Error budget remaining percentage
- **Color coding**: Based on remaining budget

#### 5. Request Volume
- **Panel**: Time series graph
- **Query**: Requests per minute
- **Threshold line**: 10,000 req/min target

#### 6. Service Health
- **Panel**: Table
- **Query**: Service status and key metrics
- **Columns**: Service, Availability, Latency, Error Rate, Status

## Alert Routing

### Severity-Based Routing
```yaml
# Critical alerts → PagerDuty → Phone call
# Warning alerts → Slack → Email
# Info alerts → Slack channel only

routes:
  - match:
      severity: critical
    receiver: pagerduty-critical
  - match:
      severity: warning
    receiver: slack-warning
  - match:
      severity: info
    receiver: slack-info
```

### Time-Based Routing
```yaml
# Business hours: All alerts to Slack
# Non-business hours: Critical to PagerDuty, others to email

routes:
  - match:
      severity: critical
    active_time_ranges:
      - start_time: "18:00"
        end_time: "09:00"
        weekdays: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    receiver: pagerduty-critical
  - receiver: slack-default
```

## SLO Compliance Reporting

### Daily Report
```python
def generate_daily_slo_report(date):
    report = {
        'date': date,
        'availability': calculate_availability(date),
        'p95_latency': calculate_p95_latency(date),
        'error_rate': calculate_error_rate(date),
        'throughput': calculate_throughput(date),
        'error_budget_remaining': calculate_remaining_budget(date),
        'slo_met': check_slo_compliance(date)
    }
    return report
```

### Weekly Report
```python
def generate_weekly_slo_report(week_start):
    report = {
        'week': week_start,
        'daily_reports': [generate_daily_slo_report(d) for d in week_days],
        'weekly_availability': calculate_weekly_availability(week_start),
        'weekly_p95_latency': calculate_weekly_p95_latency(week_start),
        'incidents': get_incidents_for_week(week_start),
        'error_budget_consumed': calculate_weekly_budget_consumption(week_start)
    }
    return report
```

### Monthly Report
```python
def generate_monthly_slo_report(month, year):
    report = {
        'month': month,
        'year': year,
        'monthly_availability': calculate_monthly_availability(month, year),
        'monthly_p95_latency': calculate_monthly_p95_latency(month, year),
        'total_incidents': get_incidents_for_month(month, year),
        'error_budget_status': calculate_monthly_budget_status(month, year),
        'trends': analyze_monthly_trends(month, year),
        'recommendations': generate_recommendations(month, year)
    }
    return report
```

## SLO Review Process

### Monthly SLO Review
- **Participants**: SRE team, Engineering leads, Product managers
- **Agenda**:
  1. Review monthly SLO performance
  2. Analyze error budget consumption
  3. Discuss major incidents
  4. Review alert effectiveness
  5. Adjust SLOs if needed
  6. Plan improvements

### Quarterly SLO Review
- **Participants**: All stakeholders
- **Agenda**:
  1. Review quarterly trends
  2. Assess SLO appropriateness
  3. Review capacity planning
  4. Discuss tooling improvements
  5. Set next quarter objectives

## SLO Adjustment Process

### When to Adjust SLOs
- Business requirements change
- Technical capabilities improve
- Cost-benefit analysis shows different target is optimal
- Customer feedback indicates need for change

### Adjustment Process
1. Propose new SLO target with justification
2. Analyze historical performance data
3. Assess impact on error budget
4. Get stakeholder approval
5. Update monitoring and alerting
6. Communicate changes to all teams
7. Monitor for 3 months before finalizing

## Continuous Improvement

### Alert Tuning
- Review alert effectiveness monthly
- Reduce false positives
- Ensure critical alerts are actionable
- Adjust thresholds based on data

### Dashboard Optimization
- Review dashboard usage
- Remove unused panels
- Add requested metrics
- Improve visualization clarity

### Process Improvement
- Gather feedback from on-call engineers
- Streamline incident response
- Improve documentation
- Automate manual processes
