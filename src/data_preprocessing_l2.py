from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length, udf, rand
from pyspark.sql.types import DoubleType
from geopy.geocoders import GoogleV3
from secrets_manager import get_parameter
import math
import time
import boto3
import pandas as pd
from datetime import datetime

def initialize_spark():
    """
    Initialize Spark session with Hadoop AWS package for S3 access.
    """
    return SparkSession.builder \
        .appName("HotelDataProcessing") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

def get_csv_file_path(s3_bucket, input_prefix):
    """
    List objects in the S3 bucket and find the CSV file.
    """
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=input_prefix)
    for obj in response.get('Contents', []):
        file_name = obj['Key']
        if file_name.endswith('.csv'):
            return f"s3a://{s3_bucket}/{file_name}"
    raise FileNotFoundError("No CSV file found in the specified S3 bucket and prefix.")

def load_and_preprocess_data(spark, csv_file_path):
    """
    Load the CSV data from S3 into a Spark DataFrame and preprocess the data.
    """
    # Load CSV data
    l1_data = spark.read.csv(csv_file_path, header=True, inferSchema=True)

    # Remove duplicates and preprocess
    l2_data = l1_data.dropDuplicates() \
        .withColumnRenamed("rating", "avg_rating") \
        .drop('review_text', 'number_of_photos', 'business_status', 'review_user') \
        .withColumn('review_length', length(col('review_text_translated'))) \
        .na.drop(subset=['review_text_translated'])

    return l2_data

def geocode_addresses(df, spark):
    """
    Geocode unique addresses and merge coordinates back to the DataFrame.
    """
    # Initialize geocoder
    GOOGLE_GEOCODING_KEY = get_parameter("GOOGLE_GEOCODING_KEY")
    geolocator = GoogleV3(api_key=GOOGLE_GEOCODING_KEY)

    def geocode_address(address):
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except Exception as e:
            print(f"Exception occurred while geocoding '{address}': {e}")
            return None, None

    # Convert Spark DataFrame to Pandas
    df_pd = df.toPandas()

    # Identify unique addresses
    unique_addresses = df_pd['address'].unique()
    unique_addresses_df = pd.DataFrame(unique_addresses, columns=['address'])

    # Geocode unique addresses
    unique_addresses_df['latitude'], unique_addresses_df['longitude'] = zip(*unique_addresses_df['address'].apply(lambda x: geocode_address(x)))
    for address in unique_addresses_df['address']:
        lat, long = geocode_address(address=address)
        time.sleep(0.1)  # Adding delay between requests

    # Merge geocoded coordinates back to the original DataFrame
    df_pd = df_pd.merge(unique_addresses_df, on='address', how='left')
    
    # Convert back to Spark DataFrame
    return spark.createDataFrame(df_pd)

def add_distance_features(df):
    """
    Add distance to nearest ski resort and city center to the DataFrame.
    """
    # Haversine formula to calculate distance
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Radius of Earth in kilometers
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # Ski resorts coordinates
    ski_resorts_coords = [
        (42.5396, 1.7336),  # Grandvalira
        (42.5558, 1.5140),  # Vallnord - Pal Arinsal
        (42.6210, 1.5230),  # Vallnord - Ordino Arcalis
        (42.4631, 1.4886)   # Naturlandia
    ]

    # UDF to calculate the minimum distance to ski resorts
    def min_distance_to_ski_resorts(lat, lon):
        distances = [haversine(lat, lon, ski_lat, ski_lon) for ski_lat, ski_lon in ski_resorts_coords]
        return min(distances)

    # Register UDF
    min_distance_udf = udf(min_distance_to_ski_resorts, DoubleType())
    df = df.withColumn("distance_to_ski_resort", min_distance_udf(col("latitude"), col("longitude")))

    # Add distance to city center
    city_center_coords = (42.5078, 1.5211)  # Coordinates for Andorra la Vella city center
    haversine_udf_city = udf(lambda lat, lon: haversine(lat, lon, city_center_coords[0], city_center_coords[1]), DoubleType())
    df = df.withColumn("distance_to_city_center", haversine_udf_city(col("latitude"), col("longitude")))

    return df

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
    input_prefix = 'l1_data/text/'
    output_prefix = 'l2_data/text/'
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Get the CSV file path from S3
    csv_file_path = get_csv_file_path(s3_bucket, input_prefix)

    # Load and preprocess data
    l2_data = load_and_preprocess_data(spark, csv_file_path)

    # Geocode addresses
    l2_data = geocode_addresses(l2_data, spark)

    # Add distance features
    l2_data = add_distance_features(l2_data)

    # Remove non-relevant columns
    l2_data = l2_data.drop('address')

    # Shuffle the DataFrame rows
    shuffled_data = l2_data.orderBy(rand())

    # Save the final data to S3
    save_to_s3(shuffled_data, s3_bucket, output_prefix, current_datetime)

    # Stop the Spark cluster
    spark.stop()

if __name__ == "__main__":
    main()