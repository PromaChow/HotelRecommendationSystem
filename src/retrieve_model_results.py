import boto3
import pandas as pd
from io import BytesIO
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')

def get_latest_file(s3_bucket, prefix, starts_with, ends_with):
    """
    Get the latest file from an S3 bucket that starts with `starts_with` and ends with `ends_with`.
    """
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in {s3_bucket} with prefix: {prefix}")

        # Filter files by starts_with and ends_with
        files = [obj for obj in response['Contents'] 
                 if obj['Key'].startswith(f"{prefix}{starts_with}") and obj['Key'].endswith(ends_with)]
        
        if not files:
            raise FileNotFoundError(f"No files found starting with {starts_with} and ending with {ends_with} in {s3_bucket}")

        # Get the latest file by LastModified date
        latest_file = max(files, key=lambda x: x['LastModified'])
        return latest_file['Key']  # Return just the S3 key (file path)
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found. Please configure your credentials.")

def load_file_from_s3(s3_bucket, file_key, file_type='csv'):
    """
    Load a file (CSV/Parquet) from S3 into a DataFrame.
    """
    response = s3.get_object(Bucket=s3_bucket, Key=file_key)
    
    if file_type == 'parquet':
        return pd.read_parquet(BytesIO(response['Body'].read()))
    elif file_type == 'csv':
        return pd.read_csv(BytesIO(response['Body'].read()))
    else:
        raise ValueError("Unsupported file type. Use 'parquet' or 'csv'.")

def load_model_training_results():
    """
    Load the latest model training results from the S3 bucket.
    """
    s3_bucket = 'andorra-hotels-data-warehouse'
    prefix = 'model_training/supervised/'
    starts_with = 'training_results'
    ends_with = '.parquet'

    try:
        # Get the latest file key
        latest_file_key = get_latest_file(s3_bucket, prefix, starts_with, ends_with)
        
        # Load the CSV file into a DataFrame
        df = load_file_from_s3(s3_bucket, latest_file_key, file_type='parquet')
        return df
    except Exception as e:
        print(f"Error loading model training results: {str(e)}")
        return None
    

df = load_model_training_results()
print(df)