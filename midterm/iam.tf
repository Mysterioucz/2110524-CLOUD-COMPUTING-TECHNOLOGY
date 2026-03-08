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

# Attach S3 Permissions to the Role
resource "aws_iam_role_policy" "wp_s3_policy" {
  name = "WordpressS3Policy"
  role = aws_iam_role.wp_s3_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket"]
      Effect   = "Allow"
      Resource = ["arn:aws:s3:::${var.bucket_name}", "arn:aws:s3:::${var.bucket_name}/*"]
    }]
  })
}

# Create the Instance Profile
resource "aws_iam_instance_profile" "wp_profile" {
  name = "WordpressProfile"
  role = aws_iam_role.wp_s3_role.name
}