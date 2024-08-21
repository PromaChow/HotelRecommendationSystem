import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("NLP Example with Spark") \
    .getOrCreate()

# Load the data
input_dir = f'input/data/training/l2_data_2024-08-20_08-36-29.parquet'
l2_data = pd.read_parquet(input_dir)

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

# Dropping the original 'region', 'hotel_name' and 'review_language' columns since we have encoded them
l2_data = l2_data.drop(['region', 'review_language', 'hotel_name'], axis=1)
# Remove the 'latitude' and 'longitude' columns
l2_data = l2_data.drop(['latitude', 'longitude'], axis=1)

# Concatenating the encoded columns with the original DataFrame
l2_data = pd.concat([l2_data, df_region_encoded, df_language_encoded], axis=1)

# Apply TF-IDF
# Pass Pandas DF to Spark DF
l3_data = spark.createDataFrame(l2_data)

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


print(l3_data.show())

spark.stop()