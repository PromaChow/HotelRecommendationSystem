# # EFS File System
# resource "aws_efs_file_system" "lambda_efs" {
#   creation_token = "lambda-efs"
#   lifecycle_policy {
#     transition_to_ia = "AFTER_30_DAYS"
#   }
#   tags = {
#     Name = "lambda_efs"
#   }
# }

# # EFS Mount Target in the same subnet as Lambda
# resource "aws_efs_mount_target" "lambda_efs_mount_target" {
#   file_system_id  = aws_efs_file_system.lambda_efs.id
#   subnet_id       = "subnet-03be3bd0296006c94"  # Replace with your actual Subnet ID
#   security_groups = [aws_security_group.lambda_sg.id]
# }

# # EFS Access Point
# resource "aws_efs_access_point" "lambda_efs_access_point" {
#   file_system_id = aws_efs_file_system.lambda_efs.id

#   posix_user {
#     gid = 1000
#     uid = 1000
#   }

#   root_directory {
#     path = "/lambda"
#     creation_info {
#       owner_gid   = 1000
#       owner_uid   = 1000
#       permissions = "755"
#     }
#   }
# }

# Security Group for Lambda to access EFS
resource "aws_security_group" "lambda_sg" {
  name        = "lambda_sg"
  description = "Security group for Lambda function to access EFS"
  vpc_id      = "vpc-023c445dc670512dc"  # Replace with your actual VPC ID

  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = ["172.31.0.0/16"]  # Adjust based on your VPC CIDR block
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}