variable "region" {
    description = "region of aws to deploy"
    type = string
}

variable "line_channel_secret" {
    description = "line channel secret"
    type = string
    sensitive = true
}

variable "line_channel_access_token" {
    description = "Line Channel access token"
    type = string
    sensitive = true
}

variable "dynamodb_table_name" {
    description = "dynamodb table name"
    type = string
    default = "PhraMonkChatHistory"
}

variable "bedrock_model_id" {
    description = "Bedrock Model ID to use"
    type = string
    default     = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
}
