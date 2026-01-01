# ElastiCache Serverless Redis
resource "aws_elasticache_serverless_cache" "redis" {
  engine = "redis"
  name   = "${var.project_name}-redis"

  cache_usage_limits {
    data_storage {
      maximum = 1
      unit    = "GB"
    }
    ecpu_per_second {
      maximum = 1000
    }
  }

  daily_snapshot_time      = "03:00"
  description              = "Serverless Redis for ${var.project_name}"
  major_engine_version     = "7"
  snapshot_retention_limit = 1
  security_group_ids       = [aws_security_group.redis.id]
  subnet_ids               = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "${var.project_name}-redis"
  }
}
