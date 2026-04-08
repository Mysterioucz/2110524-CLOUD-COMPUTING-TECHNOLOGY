
resource "aws_bedrockagent_agent" "line_agent" {
  agent_name = "line_agent"
  agent_resource_role_arn = aws_iam_role.lambda_exec.arn
  foundation_model = var.bedrock_model_id
  description = "Line Agent"
  instruction = "You are a helpful assistant designed to coordinate and manage communications through the Line messaging platform for users seeking support and guidance."
}