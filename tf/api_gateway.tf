# Create an API Gateway
resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "LambdaAPI"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]          # Allow all origins
    allow_methods = ["POST", "OPTIONS"]   # Specify allowed methods
    allow_headers = ["Content-Type"]      # Specify headers that are allowed
    expose_headers = ["*"]          # Expose all headers (optional)
    max_age = 3600                  # Cache the CORS preflight response for 1 hour
  }
}

# Create a Lambda Permission to allow API Gateway to invoke the Lambda function
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.model_inference.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/*"
}

# Create an API Gateway Integration to connect the API Gateway to the Lambda function
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.lambda_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.model_inference.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

# Create a route for the API
resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "POST /invoke"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Create a stage for the API
resource "aws_apigatewayv2_stage" "lambda_stage" {
  api_id      = aws_apigatewayv2_api.lambda_api.id
  name        = "prod"
  auto_deploy = true
}

# Output the API endpoint URL
output "api_endpoint" {
  value = "${aws_apigatewayv2_api.lambda_api.api_endpoint}/prod/invoke"
}