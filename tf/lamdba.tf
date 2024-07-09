resource "aws_lambda_function" "data_gathering" {
  function_name = "data_gathering_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_data_gathering.lambda_handler"
  runtime       = "python3.8"
  filename      = "lambda_data_gathering.zip"
}

resource "aws_lambda_permission" "allow_github" {
  statement_id  = "AllowExecutionFromGitHub"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_gathering.function_name
  principal     = "events.amazonaws.com"
}