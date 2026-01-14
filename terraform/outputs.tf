output "api_endpoint" {
  description = "Health check API endpoint"
  value       = "${module.serverless_health_check.api_endpoint}/health"
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.serverless_health_check.lambda_function_name
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = module.serverless_health_check.dynamodb_table_name
}
