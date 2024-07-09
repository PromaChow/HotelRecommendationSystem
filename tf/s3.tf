resource "aws_s3_bucket" "andorra_hotels_data_warehouse" {
  bucket = "andorra-hotels-data-warehouse"
  tags = {
    Name        = "andorra-hotels-data-warehouse"
    Environment = "Sandbox"
  }
}