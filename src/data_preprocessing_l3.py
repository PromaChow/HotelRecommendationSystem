from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
import boto3
from botocore.exceptions import NoCredentialsError
import pandas as pd
from datetime import datetime

def initialize_spark():
    """
    Initialize Spark session with Hadoop AWS package for S3 access.
    """
    return SparkSession.builder \
        .appName("HotelDataProcessingL3") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

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
        return f"s3a://{s3_bucket}/{latest_file['Key']}"
    
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

    # Dropping the original 'region', 'hotel_name', and 'review_language' columns since we have encoded them
    l2_data = l2_data.drop(['region', 'review_language', 'hotel_name'], axis=1)

    # Remove the 'latitude' and 'longitude' columns
    l2_data = l2_data.drop(['latitude', 'longitude'], axis=1)

    # Concatenating the encoded columns with the original DataFrame
    l2_data = pd.concat([l2_data, df_region_encoded, df_language_encoded], axis=1)

    return l2_data

def process_nlp(l3_data):
    """
    Perform NLP tasks: Tokenization, stopword removal, and TF-IDF.
    """
    # Tokenize and remove stopwords
    tokenizer = Tokenizer(inputCol="review_text_translated", outputCol="words")
    l3_data = tokenizer.transform(l3_data)

    remover = StopWordsRemover(inputCol="words", outputCol="filtered")
    l3_data = remover.transform(l3_data)

    # Compute TF and IDF
    hashing_tf = HashingTF(inputCol="filtered", outputCol="raw_features", numFeatures=20)
    l3_data = hashing_tf.transform(l3_data)

    idf = IDF(inputCol="raw_features", outputCol="review_text_features")
    idf_model = idf.fit(l3_data)
    l3_data = idf_model.transform(l3_data)

    # Drop intermediate columns
    l3_data = l3_data.drop('words', 'filtered', 'raw_features', 'review_text_translated')

    return l3_data

def save_to_s3(df, s3_bucket, output_prefix, current_datetime):
    """
    Save the DataFrame as a single Parquet file to S3.
    """
    # Define the temporary output path for Parquet files
    temp_output_path = f"s3a://{s3_bucket}/{output_prefix}temp_output/"
    
    # Write the DataFrame in Parquet format to the temporary output path
    df.coalesce(1).write.mode("overwrite").parquet(temp_output_path)
    
    # Initialize boto3 client
    s3 = boto3.client('s3')
    
    # List the Parquet files in the temporary output path
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=f"{output_prefix}temp_output/")
    temp_output_files = [f['Key'] for f in response.get('Contents', []) if f['Key'].endswith(".parquet")]
    
    if not temp_output_files:
        raise FileNotFoundError("No Parquet file found in the temporary output directory.")
    
    # There should be only one Parquet file in the coalesced output
    temp_parquet_file = temp_output_files[0]
    
    # Define the final output file name and path
    output_file_name = f"l2_data_{current_datetime}.parquet"
    final_output_path = f"{output_prefix}{output_file_name}"
    
    # Move the Parquet file to the final output path
    copy_source = {'Bucket': s3_bucket, 'Key': temp_parquet_file}
    s3.copy_object(CopySource=copy_source, Bucket=s3_bucket, Key=final_output_path)
    
    # Delete the temporary files and directory
    for file in temp_output_files:
        s3.delete_object(Bucket=s3_bucket, Key=file)
    s3.delete_object(Bucket=s3_bucket, Key=f"{output_prefix}temp_output/")

def main():
    # Initialize Spark session
    spark = initialize_spark()

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
    l2_data = preprocess_data(l2_data)

    # Add NLP to the text features
    l3_data = spark.createDataFrame(l2_data)
    l3_data = process_nlp(l3_data)

    # Save the final data to S3
    save_to_s3(l3_data, s3_bucket, output_prefix, current_datetime)

    # Stop the Spark cluster
    spark.stop()

if __name__ == "__main__":
    main()