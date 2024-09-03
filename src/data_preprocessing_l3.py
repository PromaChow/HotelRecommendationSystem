import boto3
from botocore.exceptions import NoCredentialsError
import pandas as pd
from datetime import datetime
import os

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
            raise FileNotFoundError(f"No Parquet files found in the specified S3 bucket: {s3_bucket} with prefix: {input_prefix}")
        
        latest_file = max(parquet_files, key=lambda x: x['LastModified'])
        return f"s3://{s3_bucket}/{latest_file['Key']}"
    
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found. Please configure your credentials.")
    
def load_data(parquet_file_path):
    """
    Load the Parquet data from S3 into a Pandas DataFrame.
    """
    l2_data = pd.read_parquet(parquet_file_path)
    return l2_data

def preprocess_data(l2_data):
    """
    Perform one-hot encoding, handle languages, assign IDs, and drop unnecessary columns.
    """
    # One-Hot Encoding for the 'region' column
    df_region_encoded = pd.get_dummies(l2_data['region'], prefix='region')

    # Handling 'review_language'
    # Calculate the percentage of each language
    language_counts = l2_data['review_language'].value_counts(normalize=True)

    # Combine languages that are less than 2% present
    languages_to_combine = language_counts[language_counts < 0.02].index
    l2_data['review_language'] = l2_data['review_language'].apply(lambda x: 'other' if x in languages_to_combine else x)

    # One-Hot Encode the remaining languages
    df_language_encoded = pd.get_dummies(l2_data['review_language'], prefix='lang')

    # Assigning IDs to 'hotel_name'
    l2_data['hotel_id'] = l2_data['hotel_name'].astype('category').cat.codes

    # Dropping the original 'region', 'review_language', and 'hotel_name' columns since we have encoded them
    l2_data = l2_data.drop(['region', 'review_language', 'hotel_name'], axis=1)

    # Remove the 'latitude' and 'longitude' columns
    l2_data = l2_data.drop(['latitude', 'longitude'], axis=1)

    # Concatenating the encoded columns with the original DataFrame
    l2_data = pd.concat([l2_data, df_region_encoded, df_language_encoded], axis=1)

    return l2_data

def save_to_s3(df, s3_bucket, output_prefix, current_datetime):
    """
    Save the DataFrame as a single Parquet file to S3 using boto3.
    """
    # Define the local temporary file path
    local_temp_path = f"/tmp/l3_data_{current_datetime}.parquet"

    # Save the DataFrame to a local Parquet file
    df.to_parquet(local_temp_path, engine='pyarrow', index=False)

    # Define the S3 output file name and path
    output_file_name = f"l3_data_{current_datetime}.parquet"
    final_output_path = f"{output_prefix}{output_file_name}"

    # Upload the local Parquet file to S3
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.upload_file(local_temp_path, s3_bucket, final_output_path)

    # Remove the local temporary file
    os.remove(local_temp_path)

def main():
    # S3 bucket details
    s3_bucket = 'andorra-hotels-data-warehouse'
    input_prefix = 'l2_data/text/'
    output_prefix = 'l3_data/text/'
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Get the Parquet file path from S3
    parquet_file_path = get_latest_parquet_file_path(s3_bucket, input_prefix)
    print(parquet_file_path)

    # Load L2 data into Pandas DataFrame
    l2_data = load_data(parquet_file_path)

    # Preprocess the data
    l3_data = preprocess_data(l2_data)

    # Save the final data to S3
    save_to_s3(l3_data, s3_bucket, output_prefix, current_datetime)

if __name__ == "__main__":
    main()