resource "aws_lambda_function" "model_inference" {
  function_name = "model_inference_lambda"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"  # Specify that this Lambda function uses a container image
  image_uri     = "${aws_ecr_repository.lambda-docker.repository_url}:latest"  # Reference the ECR image
  memory_size   = 512
  timeout       = 30
  architectures = ["arm64"] 
}

# resource "aws_lambda_function" "install_sklearn" {
#   function_name = "install_sklearn_lambda"
#   role          = aws_iam_role.lambda_role.arn
#   handler       = "install_sklearn.lambda_handler"  # Handler function from the ZIP file
#   runtime       = "python3.8"
#   filename      = "install_sklearn_lambda.zip"  # The new ZIP file
#   source_code_hash = filebase64sha256("install_sklearn_lambda.zip")
#   timeout       = 900  # 15 minutes to install scikit-learn
#   memory_size   = 1024  # Increased memory for dependency installation

#   # Attach EFS
#   file_system_config {
#     arn            = aws_efs_access_point.lambda_efs_access_point.arn
#     local_mount_path = "/mnt/efs"
#   }

#   # VPC configuration with a specified subnet
#   vpc_config {
#     subnet_ids         = ["subnet-03be3bd0296006c94"]  # Replace with your actual subnet ID
#     security_group_ids = [aws_security_group.lambda_sg.id]
#   }

#   # Ensure Lambda waits for EFS mount target to become available
#   depends_on = [aws_efs_mount_target.lambda_efs_mount_target]
# }

# resource "aws_lambda_function" "model_inference" {
#   function_name = "model_inference_lambda"
#   role          = aws_iam_role.lambda_role.arn
#   handler       = "lambda_model_inference.lambda_handler"
#   runtime       = "python3.8"
#   filename      = "lambda_model_inference.zip"
#   timeout       = 30
#   memory_size   = 512
#   layers = [
#     "arn:aws:lambda:us-west-2:336392948345:layer:AWSSDKPandas-Python38:26",
#   ]

#   # Attach EFS
#   file_system_config {
#     arn            = aws_efs_access_point.lambda_efs_access_point.arn
#     local_mount_path = "/mnt/efs"
#   }

#   # VPC configuration with a specified subnet
#   vpc_config {
#     subnet_ids         = ["subnet-03be3bd0296006c94"] 
#     security_group_ids = [aws_security_group.lambda_sg.id]
#   }

#   # Ensure Lambda waits for EFS mount target to become available
#   depends_on = [aws_efs_mount_target.lambda_efs_mount_target]
# }