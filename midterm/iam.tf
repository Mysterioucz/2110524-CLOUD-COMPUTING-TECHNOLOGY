# Create the IAM Role for the WordPress Instance
resource "aws_iam_role" "wp_s3_role" {
  name = "WordpressS3AccessRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

# Create IAM Policy for S3 access
resource "aws_iam_policy" "wp_s3_policy" {
  name        = "WordpressS3Policy"
  description = "Allow WordPress to access S3 bucket"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket", "s3:PutObjectAcl", "s3:GetBucketLocation"]
      Effect   = "Allow"
      Resource = ["arn:aws:s3:::${var.bucket_name}", "arn:aws:s3:::${var.bucket_name}/*"]
    }]
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "wp_s3_attach" {
  role       = aws_iam_role.wp_s3_role.name
  policy_arn = aws_iam_policy.wp_s3_policy.arn
}

# Create the Instance Profile
resource "aws_iam_instance_profile" "wp_profile" {
  name = "WordpressProfile"
  role = aws_iam_role.wp_s3_role.name
}