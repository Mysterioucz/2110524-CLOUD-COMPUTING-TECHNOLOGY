output "table_arn" {
  description = "The ARN of the DynamoDB table"
  value       = aws_dynamodb_table.chat_memory.arn
}
