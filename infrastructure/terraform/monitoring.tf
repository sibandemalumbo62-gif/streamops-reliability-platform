# RDS for PostgreSQL databases
resource "aws_db_subnet_group" "streamops" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = module.vpc.database_subnets

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# Auth database
resource "aws_rds_cluster" "auth_db" {
  count               = var.enable_monitoring ? 1 : 0
  engine              = "aurora-postgresql"
  engine_version      = "15.4"
  database_name       = "auth_db"
  master_username     = "streamops"
  master_password     = var.db_master_password
  db_subnet_group_name = aws_db_subnet_group.streamops.name

  vpc_security_group_ids = [aws_security_group.eks_nodes.id]

  skip_final_snapshot = true
  storage_encrypted   = true

  tags = {
    Name = "${var.project_name}-${var.environment}-auth-db"
  }
}

# ElastiCache for Redis
resource "aws_elasticache_subnet_group" "streamops" {
  name       = "${var.project_name}-${var.environment}-cache-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.project_name}-${var.environment}-cache-subnet-group"
  }
}

resource "aws_elasticache_replication_group" "streamops" {
  count               = var.enable_monitoring ? 1 : 0
  replication_group_id = "${var.project_name}-${var.environment}-redis"
  description          = "Redis cluster for StreamOps"
  node_type           = "cache.t3.micro"
  num_cache_clusters  = 2
  engine              = "redis"
  engine_version      = "7.0"
  port                = 6379

  subnet_group_name  = aws_elasticache_subnet_group.streamops.name
  security_group_ids = [aws_security_group.eks_nodes.id]

  automatic_failover_enabled = true
  multi_az_enabled           = true

  tags = {
    Name = "${var.project_name}-${var.environment}-redis"
  }
}

# CloudWatch alarms for monitoring
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "cpu_utilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"

  alarm_description = "This metric monitors EKS node CPU utilization"
  alarm_actions     = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = module.eks.cluster_name
  }
}

resource "aws_cloudwatch_metric_alarm" "memory_high" {
  alarm_name          = "${var.project_name}-${var.environment}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "memory_utilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"

  alarm_description = "This metric monitors EKS node memory utilization"
  alarm_actions     = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = module.eks.cluster_name
  }
}

# SNS topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-alerts"
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
