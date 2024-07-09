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
  description = "IAM policy for Lambda to access S3 and Parameter Store"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ssm:GetParameter",
          "s3:PutObject"
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