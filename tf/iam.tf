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

# IAM Role for Glue Job
resource "aws_iam_role" "glue_role" {
  name = "glue_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "glue.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM Policy for Glue Job
resource "aws_iam_role_policy_attachment" "glue_policy" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# IAM Policy for Glue Job to access S3 bucket
resource "aws_iam_policy" "glue_s3_access_policy" {
  name        = "GlueS3AccessPolicy"
  description = "IAM policy for Glue job to access S3 bucket"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:PutBucketPolicy",
          "s3:GetBucketPolicy"
        ],
        Resource = [
          "arn:aws:s3:::andorra-hotels-data-warehouse",
          "arn:aws:s3:::andorra-hotels-data-warehouse/*"
        ]
      }
    ]
  })
}

# Attach the S3 access policy to the Glue role
resource "aws_iam_role_policy_attachment" "glue_s3_policy_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.glue_s3_access_policy.arn
}