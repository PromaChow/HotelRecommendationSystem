resource "aws_ecr_repository" "lambda-docker" {
  name = "lambda-docker"

  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

# Fetch the ECR login credentials
data "aws_ecr_authorization_token" "ecr_auth" {}

# Get the account ID (for constructing the ECR repo URL)
data "aws_caller_identity" "current" {}

# Build and push the Docker image using a local-exec provisioner
resource "null_resource" "docker_image_push" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.us-west-2.amazonaws.com

      docker build --provenance=false -t lambda-docker ./lambda_docker
      docker tag lambda-docker:latest ${aws_ecr_repository.lambda-docker.repository_url}:latest
      docker push ${aws_ecr_repository.lambda-docker.repository_url}:latest
    EOT
  }

  depends_on = [aws_ecr_repository.lambda-docker]
}