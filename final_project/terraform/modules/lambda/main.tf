# Lambda Function
resource "aws_lambda_function" "backend" {
  function_name = "PhraMonk-Backend"
  role          = var.lambda_role_arn
  handler       = "src.lambda_function.lambda_handler" # main.py -> lambda_handler()
  runtime       = "python3.11"
  filename = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout = 60
  memory_size = 256

  environment {
    variables = {
      LINE_CHANNEL_SECRET       = var.line_channel_secret
      LINE_CHANNEL_ACCESS_TOKEN = var.line_channel_access_token
      DYNAMODB_TABLE_NAME       = var.dynamodb_table_name
      BEDROCK_MODEL_ID          = var.bedrock_model_id
    }
  }
}

# Run setup script to install dependencies and stage code
resource "null_resource" "build_package" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "${path.module}/../../scripts/setup.sh"
  }
}

data "archive_file" "lambda_zip" {
  depends_on = [ null_resource.build_package ]
  type = "zip"
  source_dir = "${path.module}/../../dist"
  output_path = "${path.module}/../../phramonk_lambda.zip"
}