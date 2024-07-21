import re
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, regexp_replace, lit, size, udf, lower
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, MapType
from langdetect import detect, LangDetectException
from googletrans import Translator
import boto3

def initialize_spark():
    return SparkSession.builder \
        .appName("HotelDataProcessing") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

def get_schema():
    return StructType([
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

def convert_to_days(date_str):
    try:
        if "day" in date_str:
            days = int(re.findall(r'\d+', date_str)[0])
        elif "week" in date_str:
            days = int(re.findall(r'\d+', date_str)[0]) * 7
        elif "month" in date_str:
            days = int(re.findall(r'\d+', date_str)[0]) * 30
        elif "year" in date_str:
            days = int(re.findall(r'\d+', date_str)[0]) * 365
        else:
            days = 0
    except (ValueError, IndexError):
        days = 0
    return days

convert_to_days_udf = udf(convert_to_days, IntegerType())

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'unknown'

detect_language_udf = udf(detect_language, StringType())

def process_reviews(df, schema):
    exploded_df = df.select(
        col("hotel_name"),
        col("rating"),
        col("user_ratings_total"),
        col("address"),
        col("business_status"),
        size(col("photos")).alias("number_of_photos"),  # Add column for number of photos
        explode(col("reviews")).alias("review")
    )

    flattened_df = exploded_df.select(
        lit(region).alias("region"),  # Add region as a new column
        col("hotel_name"),
        col("rating"),
        col("user_ratings_total"),
        col("number_of_photos"),  # Include the number of photos column
        col("address"),
        col("business_status"),
        col("review.user").alias("review_user"),
        col("review.rating").alias("review_rating"),
        convert_to_days_udf(col("review.date")).alias("review_date_in_days"),  # Convert review date to days
        lower(regexp_replace(regexp_replace(regexp_replace(col("review.review"), "\n", ""), "\r", ""), "[^a-zA-Z0-9\s]", "")).alias("review_text"),
        detect_language_udf(col("review.review")).alias("review_language")  # Detect language
    )

    flattened_pdf = flattened_df.toPandas()

    translator = Translator()
    for index, row in flattened_pdf.iterrows():
        if row['review_language'] != 'en' and row['review_language'] != 'unknown':
            try:
                translated_text = translator.translate(row['review_text'], dest='en').text
                flattened_pdf.at[index, 'review_text_translated'] = translated_text
            except Exception as e:
                flattened_pdf.at[index, 'review_text_translated'] = row['review_text']
        else:
            flattened_pdf.at[index, 'review_text_translated'] = row['review_text']

    translated_df = spark.createDataFrame(flattened_pdf, schema=empty_df_schema)
    return translated_df

def save_to_s3(df, s3_bucket, output_prefix, current_datetime):
    temp_output_path = f"s3a://{s3_bucket}/{output_prefix}temp_output/"
    df.write.mode("overwrite").csv(temp_output_path, header=True)

    s3 = boto3.client('s3')
    temp_output_files = [f['Key'] for f in s3.list_objects_v2(Bucket=s3_bucket, Prefix=f"{output_prefix}temp_output/").get('Contents', []) if f['Key'].endswith(".csv")]

    output_file_name = f"l1_data_{current_datetime}.csv"
    final_output_path = f"{output_prefix}{output_file_name}"

    if temp_output_files:
        for file in temp_output_files:
            copy_source = {'Bucket': s3_bucket, 'Key': file}
            s3.copy_object(CopySource=copy_source, Bucket=s3_bucket, Key=final_output_path)
            s3.delete_object(Bucket=s3_bucket, Key=file)

    s3.delete_object(Bucket=s3_bucket, Key=f"{output_prefix}temp_output/")

def main():
    global spark, region, empty_df_schema
    spark = initialize_spark()

    s3_bucket = 'andorra-hotels-data-warehouse'
    input_prefix = 'raw_data/text/'
    output_prefix = 'l1_data/text/'
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    schema = get_schema()
    empty_df_schema = StructType([
        StructField("region", StringType(), True),
        StructField("hotel_name", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("user_ratings_total", IntegerType(), True),
        StructField("number_of_photos", IntegerType(), True),
        StructField("address", StringType(), True),
        StructField("business_status", StringType(), True),
        StructField("review_user", StringType(), True),
        StructField("review_rating", StringType(), True),
        StructField("review_date_in_days", IntegerType(), True),
        StructField("review_text", StringType(), True),
        StructField("review_language", StringType(), True),
        StructField("review_text_translated", StringType(), True)
    ])

    combined_df = spark.createDataFrame([], empty_df_schema)

    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=input_prefix)

    for obj in response.get('Contents', []):
        file_name = obj['Key']
        if file_name.endswith('.json'):
            region = file_name.split('/')[-1].split('_')[0]
            json_file_path = f"s3a://{s3_bucket}/{file_name}"
            df = spark.read.schema(schema).option("multiline", "true").json(json_file_path)
            translated_df = process_reviews(df, empty_df_schema)
            combined_df = combined_df.unionByName(translated_df)

    combined_df = combined_df.coalesce(1)
    save_to_s3(combined_df, s3_bucket, output_prefix, current_datetime)

    spark.stop()

if __name__ == "__main__":
    main()