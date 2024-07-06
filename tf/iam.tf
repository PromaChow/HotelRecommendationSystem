resource "aws_iam_user" "admin_user" {
  name = "normagutiesc@gmail.com"
}

resource "aws_iam_policy" "s3_access_policy" {
  name        = "S3AccessPolicy"
  description = "IAM policy for Terraform to access S3 bucket"
  policy      = jsonencode({
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