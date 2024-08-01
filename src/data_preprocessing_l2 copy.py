from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import col, udf, rand
from geopy.geocoders import GoogleV3
from secrets_manager import get_parameter
import math
import time
import boto3
import pandas as pd
from datetime import datetime

# Initialize Spark session with Hadoop AWS package
def initialize_spark():
    return SparkSession.builder \
        .appName("HotelDataProcessing") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()
spark = initialize_spark()

# S3 bucket details
s3_bucket = 'andorra-hotels-data-warehouse'
input_prefix = 'l1_data/text/'
output_prefix = 'l2_data/text/'
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Use boto3 to list objects in the S3 bucket
s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=input_prefix)

# Find the CSV file in the S3 bucket
csv_file_path = None
for obj in response.get('Contents', []):
    file_name = obj['Key']
    if file_name.endswith('.csv'):
        csv_file_path = f"s3a://{s3_bucket}/{file_name}"
        break

if csv_file_path is None:
    raise FileNotFoundError("No CSV file found in the specified S3 bucket and prefix.")

# Load the CSV data from S3 into a Spark DataFrame
l1_data = spark.read.csv(csv_file_path, header=True, inferSchema=True)

# Remove duplicates
l2_data = l1_data.dropDuplicates()

# Average Rating per hotel
# Rename Rating column to avg_rating
l2_data = l2_data.withColumnRenamed("rating", "avg_rating")

# Delete non relevant columns: review_text, number_of_photos, business_status, review_user
l2_data = l1_data.drop('review_text', 'number_of_photos', 'business_status', 'review_user')

# Review length
l2_data = l2_data.withColumn('review_length', length(col('review_text_translated')))

# Handle missing values
l2_data = l2_data.na.drop(subset=['review_text_translated'])

# Tokenize the text
tokenizer = Tokenizer(inputCol="review_text_translated", outputCol="words")
l2_data = tokenizer.transform(l2_data)

# Remove stopwords
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
l2_data = remover.transform(l2_data)

# Compute TF (Term Frequency)
hashing_tf = HashingTF(inputCol="filtered", outputCol="raw_features", numFeatures=20)
l2_data = hashing_tf.transform(l2_data)

# Compute IDF (Inverse Document Frequency)
idf = IDF(inputCol="raw_features", outputCol="review_text_features")
idf_model = idf.fit(l2_data)
l2_data = idf_model.transform(l2_data)

# Delete non relevant columns: words, filtered, raw_features
l2_data = l2_data.drop('words', 'filtered', 'raw_features')

# Initialize geocoder with your Google API key
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
    
# Convert Spark DataFrame to Pandas for geocoding
l2_data_pd = l2_data.toPandas()

# Identify unique addresses
unique_addresses = l2_data_pd['address'].unique()

# Create a DataFrame for unique addresses
unique_addresses_df = pd.DataFrame(unique_addresses, columns=['address'])

# Geocode unique addresses with a delay to avoid rate limiting
unique_addresses_df['latitude'], unique_addresses_df['longitude'] = zip(*unique_addresses_df['address'].apply(lambda x: geocode_address(x)))
print(len(unique_addresses_df))
for address in unique_addresses_df['address']:
    lat, long = geocode_address(address=address)
    time.sleep(0.1)  # Adding delay between requests

# Merge geocoded coordinates back to the original DataFrame
l2_data_pd = l2_data_pd.merge(unique_addresses_df, on='address', how='left')

# Convert back to Spark DataFrame
l2_data = spark.createDataFrame(l2_data_pd)

# Haversine formula to calculate the distance
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

# Add distance to nearest ski resort
l2_data = l2_data.withColumn("distance_to_ski_resort", min_distance_udf(col("latitude"), col("longitude")))

# Assuming the dataset includes 'latitude' and 'longitude' columns
# Add distance to city center
city_center_coords = (42.5078, 1.5211) # Coordinates for Andorra la Vella city center
haversine_udf_city = udf(lambda lat, lon: haversine(lat, lon, city_center_coords[0], city_center_coords[1]), DoubleType())
l2_data = l2_data.withColumn("distance_to_city_center", haversine_udf_city(col("latitude"), col("longitude")))

# Remove non-relevant columns
l2_data = l2_data.drop('address', "review_text_translated")

# Shuffle the DataFrame rows
shuffled_data = l2_data.orderBy(rand())

# def save_to_s3(df, s3_bucket, output_prefix, current_datetime):
#     # Define the output path for the Parquet file
#     output_file_name = f"l2_data_{current_datetime}.parquet"
#     final_output_path = f"s3a://{s3_bucket}/{output_prefix}{output_file_name}"
    
#     # Coalesce the DataFrame to a single partition to get a single Parquet file
#     df.coalesce(1).write.mode("overwrite").parquet(final_output_path)

def save_to_s3(df, s3_bucket, output_prefix, current_datetime):
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

# Write the final data to a CSV file
save_to_s3(l2_data, s3_bucket, output_prefix, current_datetime)

# Stop the Spark cluster
spark.stop()