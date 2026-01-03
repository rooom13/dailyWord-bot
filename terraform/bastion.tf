# # Temporary Bastion Host for Redis Access
# # Comment out this entire file when you no longer need bastion access

# # Data source to get the latest Amazon Linux 2023 AMI
# data "aws_ami" "amazon_linux" {
#   most_recent = true
#   owners      = ["amazon"]

#   filter {
#     name   = "name"
#     values = ["al2023-ami-*-x86_64"]
#   }

#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }
# }

# # IAM Role for bastion to allow SSM access
# resource "aws_iam_role" "bastion" {
#   name = "${var.project_name}-bastion-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = { Service = "ec2.amazonaws.com" }
#     }]
#   })
# }

# # Attach SSM policy to bastion role
# resource "aws_iam_role_policy_attachment" "bastion_ssm" {
#   role       = aws_iam_role.bastion.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
# }

# # Instance profile for bastion
# resource "aws_iam_instance_profile" "bastion" {
#   name = "${var.project_name}-bastion-profile"
#   role = aws_iam_role.bastion.name
# }

# # Security group for bastion host
# resource "aws_security_group" "bastion" {
#   name        = "${var.project_name}-bastion-sg"
#   description = "Security group for temporary bastion host"
#   vpc_id      = aws_vpc.main.id

#   # Allow SSH from anywhere (restrict to your IP if needed)
#   ingress {
#     description = "SSH access"
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   # Allow all outbound traffic
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags = {
#     Name = "${var.project_name}-bastion-sg"
#   }
# }

# # EC2 bastion instance
# resource "aws_instance" "bastion" {
#   ami                         = data.aws_ami.amazon_linux.id
#   instance_type               = "t3.micro"
#   subnet_id                   = aws_subnet.public.id
#   vpc_security_group_ids      = [aws_security_group.bastion.id]
#   associate_public_ip_address = true
#   iam_instance_profile        = aws_iam_instance_profile.bastion.name

#   user_data = <<-EOF
#               #!/bin/bash
#               yum update -y
#               yum install -y redis6
#               EOF

#   tags = {
#     Name = "${var.project_name}-bastion"
#   }
# }

# # Security group rule to allow bastion to access Redis
# resource "aws_security_group_rule" "redis_bastion_access" {
#   type                     = "ingress"
#   description              = "Temporary access from bastion EC2 for migration/debugging"
#   from_port                = 6379
#   to_port                  = 6379
#   protocol                 = "tcp"
#   source_security_group_id = aws_security_group.bastion.id
#   security_group_id        = aws_security_group.redis.id
# }



# output "bastion_instance_id" {
#   value       = try(aws_instance.bastion.id, "Bastion not created")
#   description = "Instance ID of the bastion host (if created)"
# }

# output "bastion_public_ip" {
#   value       = try(aws_instance.bastion.public_ip, "Bastion not created")
#   description = "Public IP of the bastion host (if created)"
# }

# output "bastion_ssh_command" {
#   value       = try("ssh -i your-key.pem ec2-user@${aws_instance.bastion.public_ip}", "Bastion not created")
#   description = "SSH command to connect to bastion (if created)"
# }

# output "bastion_ssm_command" {
#   value       = try("aws ssm start-session --target ${aws_instance.bastion.id} --region ${var.aws_region}", "Bastion not created")
#   description = "SSM Session Manager command (no SSH key needed)"
# }

# output "redis_connect_command" {
#   value       = try("redis-cli -h ${aws_elasticache_serverless_cache.redis.endpoint[0].address} --tls", "Connect command for Redis")
#   description = "Redis connection command from bastion"
# }
