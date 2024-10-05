resource "aws_lambda_function" "model_inference" {
  function_name = "model_inference_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_model_inference.lambda_handler"
  runtime       = "python3.8"
  filename      = "lambda_model_inference.zip"
  timeout       = 30
  layers = [
    "arn:aws:lambda:us-west-2:336392948345:layer:AWSSDKPandas-Python38:26",
  ]
}

# resource "aws_lambda_permission" "allow_github" {
#   statement_id  = "AllowExecutionFromGitHub"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.lambda_model_inference.function_name
#   principal     = "events.amazonaws.com"
# }