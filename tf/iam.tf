resource "aws_iam_user" "admin_user" {
  name = "normagutiesc@gmail.com"
}

# IAM role for S3
resource "aws_iam_policy" "s3_access_policy" {
  name        = "S3AccessPolicy"
  description = "IAM policy for Terraform to access S3 bucket"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:ListBucket"],
        Resource = ["arn:aws:s3:::andorra-hotels-data-warehouse"]
      },
      {
        Effect   = "Allow",
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
        Resource = ["arn:aws:s3:::andorra-hotels-data-warehouse/*"]
      },
      {
        Effect   = "Allow",
        Action   = ["s3:CreateBucket", "s3:DeleteBucket", "s3:PutBucketPolicy", "s3:GetBucketPolicy"],
        Resource = ["arn:aws:s3:::andorra-hotels-data-warehouse"]
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "s3_access_policy_attachment_user" {
  name       = "S3AccessPolicyAttachment"
  policy_arn = aws_iam_policy.s3_access_policy.arn
  users      = [aws_iam_user.admin_user.name]
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "LambdaPolicy"
  description = "IAM policy for Lambda to access S3, EC2, EFS, ECR, and update Lambda code"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",    # This allows Lambda to read objects from S3
          "s3:ListBucket",   # This allows Lambda to list the contents of the S3 bucket
          "s3:PutObject",    # If Lambda needs to write back to S3
          "ssm:GetParameter" # If you're fetching any parameters from AWS SSM
        ],
        Resource = [
          "arn:aws:s3:::andorra-hotels-data-warehouse",  # Bucket permission
          "arn:aws:s3:::andorra-hotels-data-warehouse/*" # Object-level permission
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "lambda:GetLayerVersion"  # Grant permission to access Lambda layers
        ],
        Resource = [
          "arn:aws:lambda:us-west-2:336392948345:layer:AWSSDKPandas-Python38:*", 
        ]
      },
      # Permissions for updating Lambda function code
      {
        Effect = "Allow",
        Action = [
          "lambda:GetFunctionConfiguration", # To check the current Lambda configuration
          "lambda:UpdateFunctionCode"        # To update the Lambda function's image URI
        ],
        Resource = "arn:aws:lambda:us-west-2:<your-account-id>:function:model_inference_lambda" # Replace with your actual Lambda function ARN
      },
      # ECR permissions to describe and pull images
      {
        Effect = "Allow",
        Action = [
          "ecr:DescribeImages",       # To get the latest image URI from ECR
          "ecr:GetDownloadUrlForLayer", # To pull the Docker image layers
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetAuthorizationToken" # Authorization to access ECR
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_policy_attachment" {
  name       = "LambdaPolicyAttachment"
  policy_arn = aws_iam_policy.lambda_policy.arn
  roles      = [aws_iam_role.lambda_role.name]
}