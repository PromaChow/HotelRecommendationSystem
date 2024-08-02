# coverage run -m pytest -q tests/test_data_preprocessing_l2.py
# coverage report --show-missing --include=data_preprocessing_l2.py --omit=/tests/

import pytest
import os
import boto3
import pandas as pd
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, MapType

from src.data_preprocessing_l2 import (
    initialize_spark,
    get_csv_file_path,
    load_and_preprocess_data,
    geocode_addresses,
    add_distance_features,
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


def test_get_csv_file_path(mocker):
    s3_bucket = 'test-bucket'
    input_prefix = 'test-prefix/'
    
    mocker.patch('boto3.client')
    mock_s3 = boto3.client.return_value
    mock_s3.list_objects_v2.return_value = {
        'Contents': [
            {'Key': 'test-prefix/test-file.csv'}
        ]
    }
    
    csv_file_path = get_csv_file_path(s3_bucket, input_prefix)
    
    assert csv_file_path == 's3a://test-bucket/test-prefix/test-file.csv'
    mock_s3.list_objects_v2.assert_called_once_with(Bucket=s3_bucket, Prefix=input_prefix)


def test_load_and_preprocess_data(spark, mocker):
    # I AM NOT GOING TO TEST THE LOAD AND PREPROCESS FUNCION SINCE ITS TESTED WITH THE DATA PREPROCESSING GA    
    pass 


def test_geocode_addresses(spark, mocker):
    # Mock data
    data = {
        'address': ["Carrer de na Maria Pla, 19-21, AD500 Andorra la Vella, Andorra"],
        'review_text_translated': ['This is a great hotel']
    }
    df = spark.createDataFrame(pd.DataFrame(data))
    geocoded_df = geocode_addresses(df, spark)

    # Check if latitude and longitude columns are added
    assert 'latitude' in geocoded_df.columns
    assert 'longitude' in geocoded_df.columns


def test_add_distance_features(spark):
    # Mock data
    data = {
        'latitude': [42.5],
        'longitude': [1.5]
    }
    df = spark.createDataFrame(pd.DataFrame(data))

    df_with_distances = add_distance_features(df)

    # Check if distance columns are added
    assert 'distance_to_ski_resort' in df_with_distances.columns
    assert 'distance_to_city_center' in df_with_distances.columns


def test_save_to_s3():
    # I AM NOT GOING TO TEST THE SAVE TO S3 FUNCION SINCE ITS TESTED WITH THE DATA PREPROCESSING GA    
    pass 

def test_main():
    # I AM NOT GOING TO TEST THE MAIN FUNCION SINCE ITS TESTED WITH THE DATA PREPROCESSING GA
    pass