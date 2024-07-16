resource "aws_glue_job" "etl_job" {
  name     = "hotel_data_preprocessing_job"
  role_arn = aws_iam_role.glue_role.arn
  command {
    script_location = "s3://andorra-hotels-data-warehouse/scripts/data_preprocessing.py"
    python_version  = "3"
  }

  default_arguments = {
    "--TempDir" = "s3://andorra-hotels-data-warehouse/temp/"
  }
  max_retries  = 1
  max_capacity = 2
}