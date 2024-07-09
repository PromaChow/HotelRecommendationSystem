# Terraform Configuration for AWS
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket = "andorra-hotels-data-warehouse"
    key    = "hotelrecomendationsystem/terraform/tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
}