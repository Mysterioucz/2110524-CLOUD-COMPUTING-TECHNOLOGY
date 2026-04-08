terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
        source = "hashicorp/archive"
        version = "~> 2.4"
    }
    null = {
        source = "hashicorp/null"
        version = "~> 3.2"
    }
  }

  backend "s3" {
    bucket = "phra-monk-tfstate"
    key = "prod/terraform.tfstate"
    region = "ap-southeast-7"
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
        Project = "PhraMonk-Backend"
        ManagedBy = "OpenTofu"
    }
  }
}


module "lambda" {
  source = "./modules/lambda"

  line_channel_secret       = var.line_channel_secret
  line_channel_access_token = var.line_channel_access_token
  bedrock_model_id          = var.bedrock_model_id
  dynamodb_table_name = var.dynamodb_table_name

  lambda_role_arn           = aws_iam_role.lambda_exec.arn

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy_attachment.lambda_custom_attachment,
  ]
}

module "dynamodb" {
  source = "./modules/db"

  dynamodb_table_name       = var.dynamodb_table_name
}

module "api_gateway" {
  source = "./modules/api_gateway"

  lambda_invoke_arn    = module.lambda.invoke_arn
  lambda_function_name = module.lambda.lambda_function_name

  depends_on = [
    module.lambda,
  ]
}