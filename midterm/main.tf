resource "aws_vpc" "main" {
  cidr_block = "172.16.0.0/16"
  tags       = { Name = "VPC" }
}

resource "aws_subnet" "app_inet" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "172.16.1.0/24"
  availability_zone = var.availability_zone_a
  tags              = { Name = "App-Inet" }
}

resource "aws_subnet" "app_db_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "172.16.2.0/24"
  availability_zone = var.availability_zone_a
  tags              = { Name = "App-DB A" }
}

resource "aws_subnet" "app_db_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "172.16.3.0/24"
  availability_zone = var.availability_zone_b
  tags              = { Name = "App-DB B" }
}

resource "aws_db_subnet_group" "main" {
  name       = "main"
  subnet_ids = [aws_subnet.app_db_a.id, aws_subnet.app_db_b.id]
  tags       = { Name = "My DB subnet group" }
}

resource "aws_instance" "wordpress" {
  ami                  = var.ami
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.wp_profile.name

  subnet_id              = aws_subnet.app_inet.id
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = templatefile("install-wp.sh", {
    db_pass     = var.database_pass,
    db_user     = var.database_user,
    db_name     = var.database_name,
    db_host     = aws_db_instance.database.address,
    admin_user  = var.admin_user,
    admin_pass  = var.admin_pass,
    bucket_name = var.bucket_name,
    region      = var.region
  })
  tags = { Name = "Wordpress-App" }
}

resource "aws_db_instance" "database" {
  engine                 = "mariadb"
  engine_version         = "11.8.5"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  publicly_accessible    = false
  skip_final_snapshot    = true
  db_name                = var.database_name
  username               = var.database_user
  password               = var.database_pass
}
resource "aws_s3_bucket" "wp_media" {
  bucket        = var.bucket_name
  force_destroy = true
  tags          = { Name = "Wordpress-Media-Bucket" }
}

resource "aws_s3_bucket_ownership_controls" "wp_media" {
  bucket = aws_s3_bucket.wp_media.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "wp_media" {
  bucket = aws_s3_bucket.wp_media.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "wp_media_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.wp_media,
    aws_s3_bucket_public_access_block.wp_media,
  ]

  bucket = aws_s3_bucket.wp_media.id
  acl    = "public-read"
}
