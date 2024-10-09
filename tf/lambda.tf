resource "aws_lambda_function" "model_inference" {
  function_name = "model_inference_lambda"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"  # Specify that this Lambda function uses a container image
  image_uri     = "${aws_ecr_repository.lambda-docker.repository_url}:latest"  # Reference the ECR image
  memory_size   = 512
  timeout       = 30
  architectures = ["arm64"] 
}