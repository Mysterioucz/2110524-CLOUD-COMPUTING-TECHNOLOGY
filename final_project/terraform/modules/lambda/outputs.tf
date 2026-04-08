output "lambda_function_name" {
  description = "The Lambda function name"
  value       = aws_lambda_function.backend.function_name
}

output "invoke_arn" {
  description = "The Invoke ARN for the Lambda function"
  value       = aws_lambda_function.backend.invoke_arn
}