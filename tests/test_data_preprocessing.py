# coverage run -m pytest -q tests/test_data_preprocessing.py
# coverage report --show-missing --include=data_preprocessing.py --omit=/tests/

import pytest
import os
import boto3
import pandas as pd
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, MapType

from src.data_preprocessing_l1 import (
    initialize_spark,
    get_schema,
    convert_to_days,
    detect_language,
    process_reviews,
    save_to_s3,
    main
)

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .appName("pytest-spark") \
        .master("local[2]") \
        .getOrCreate()


def test_initialize_spark():
    spark = initialize_spark()
    # Check if the Spark session is created
    assert spark is not None
    # Check the app name
    assert spark.conf.get("spark.app.name") == "HotelDataProcessing"
    # Check specific configurations
    assert spark.conf.get("spark.jars.packages") == "org.apache.hadoop:hadoop-aws:3.3.1"
    assert spark.conf.get("spark.hadoop.fs.s3a.impl") == "org.apache.hadoop.fs.s3a.S3AFileSystem"
    assert spark.conf.get("spark.hadoop.fs.s3a.aws.credentials.provider") == "com.amazonaws.auth.DefaultAWSCredentialsProviderChain"
    assert spark.conf.get("spark.hadoop.fs.s3a.endpoint") == "s3.amazonaws.com"
    # Stop the Spark session after the test
    spark.stop()

def test_get_schema():
    schema = get_schema()
    # Define the expected schema
    expected_schema = StructType([
        StructField("hotel_name", StringType(), True),
        StructField("location", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("user_ratings_total", IntegerType(), True),
        StructField("max_number_of_people", IntegerType(), True),
        StructField("address", StringType(), True),
        StructField("business_status", StringType(), True),
        StructField("place_id", StringType(), True),
        StructField("amenities", MapType(StringType(), StringType()), True),
        StructField("photos", ArrayType(
            StructType([
                StructField("photo_reference", StringType(), True),
                StructField("s3_url", StringType(), True),
                StructField("html_attributions", ArrayType(StringType()), True)
            ])
        ), True),
        StructField("reviews", ArrayType(
            StructType([
                StructField("user", StringType(), True),
                StructField("rating", StringType(), True),
                StructField("date", StringType(), True),
                StructField("review", StringType(), True)
            ])
        ), True),
        StructField("source", StringType(), True)
    ])
    # Assert the schema matches the expected schema
    assert schema == expected_schema

def test_convert_to_days():
    assert convert_to_days("5 days ago") == 5
    assert convert_to_days("2 weeks ago") == 14
    assert convert_to_days("1 month ago") == 30
    assert convert_to_days("1 year ago") == 365
    assert convert_to_days("unknown") == 0

def test_detect_language():
    assert detect_language("This is an English text") == "en"
    assert detect_language("Ceci est un texte français") == "fr"
    assert detect_language("未知的语言") == "zh-cn"
    assert detect_language("") == "unknown"

def test_process_reviews():
    # I AM NOT GOING TO TEST THE MAIN FUNCION SINCE ITS TESTED WITH THE DATA PREPROCESSING GA   
    pass

def test_save_to_s3():
    # I AM NOT GOING TO TEST THE MAIN FUNCION SINCE ITS TESTED WITH THE DATA PREPROCESSING GA    
    pass 

def test_main():
    # I AM NOT GOING TO TEST THE MAIN FUNCION SINCE ITS TESTED WITH THE DATA PREPROCESSING GA
    pass