import pandas as pd
import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO

def get_latest_parquet_file_path(s3_bucket, input_prefix):
    """
    List objects in the S3 bucket, find the latest Parquet file based on the LastModified timestamp.
    """
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=input_prefix)
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in the specified S3 bucket: {s3_bucket} with prefix: {input_prefix}")

        # Filter for Parquet files and sort by LastModified date
        parquet_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.parquet')]
        if not parquet_files:
            raise FileNotFoundError(f"No Parquet files found in the specified S3 bucket: {s3_bucket} with prefix:  {input_prefix}")
        
        latest_file = max(parquet_files, key=lambda x: x['LastModified'])
        return f"s3://{s3_bucket}/{latest_file['Key']}"
    
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found. Please configure your credentials.")


def load_data(parquet_file_path):
    """
    Load the Parquet data from S3 into a Pandas DataFrame.
    """
    data = pd.read_parquet(parquet_file_path)
    return data


# Function to get the latest file from S3
def get_latest_file(s3_bucket, prefix, starts_with, ends_with):
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in {s3_bucket} with prefix: {prefix}")

        files = [obj for obj in response['Contents'] if obj['Key'].startswith(f"{prefix}{starts_with}") and obj['Key'].endswith(ends_with)]
        if not files:
            raise FileNotFoundError(f"No files found starting with {starts_with} and ending with {ends_with} in {s3_bucket}")

        latest_file = max(files, key=lambda x: x['LastModified'])
        return latest_file['Key']  # Return just the S3 key
    except Exception as e:
        st.error(f"Error fetching the file from S3: {e}")
        return None

# Function to load a CSV file from S3
def load_file_from_s3(s3_bucket, file_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=s3_bucket, Key=file_key)
    return pd.read_csv(BytesIO(response['Body'].read()))