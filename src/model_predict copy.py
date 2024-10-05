import pandas as pd
import pickle
import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO


def get_latest_file(s3_bucket, prefix, starts_with, ends_with):
    """
    Get the latest file from an S3 bucket that starts with `starts_with` and ends with `ends_with`.
    """
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in {s3_bucket} with prefix: {prefix}")

        # Filter files based on the given start and end criteria
        files = [obj for obj in response['Contents'] if obj['Key'].startswith(f"{prefix}{starts_with}") and obj['Key'].endswith(ends_with)]
        if not files:
            raise FileNotFoundError(f"No files found starting with {starts_with} and ending with {ends_with} in {s3_bucket}")

        # Return the latest file based on LastModified timestamp
        latest_file = max(files, key=lambda x: x['LastModified'])
        return latest_file['Key']  # Return just the S3 key
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found. Please configure your credentials.")


def load_file_from_s3(s3_bucket, file_key, file_type='parquet'):
    """
    Load a file (Parquet/CSV) from S3 into a DataFrame.
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=s3_bucket, Key=file_key)
    
    if file_type == 'parquet':
        return pd.read_parquet(BytesIO(response['Body'].read()))
    elif file_type == 'csv':
        return pd.read_csv(BytesIO(response['Body'].read()))
    else:
        raise ValueError("Unsupported file type. Use 'parquet' or 'csv'.")


def load_model_from_s3(s3_bucket, model_key):
    """
    Load a model (Pickle file) from S3.
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=s3_bucket, Key=model_key)
    return pickle.load(BytesIO(response['Body'].read()))


def get_hotel_id_from_name(hotel_name, hotel_map):
    """
    Get the hotel_id for a given hotel name.
    """
    match = hotel_map[hotel_map['hotel_name'] == hotel_name]
    if match.empty:
        return None
    return match['hotel_id'].values[0]


def predict_hotel_rating(hotel_name, hotel_map, val_data, model, scaler):
    """
    Given a hotel name, predict the average rating using the provided model and scaler.
    """
    # Step 1: Get hotel_id from the hotel name
    hotel_id = get_hotel_id_from_name(hotel_name, hotel_map)
    if hotel_id is None:
        return f"No hotel found with the name: {hotel_name}"
    
    # Step 2: Get all rows for the hotel using hotel_id
    hotel_data_rows = val_data[val_data['hotel_id'] == hotel_id]
    if hotel_data_rows.empty:
        return f"No data found for hotel ID: {hotel_id}"
    
    # Step 3: Prepare the data for prediction (drop target)
    X_hotel = hotel_data_rows.drop(columns=['avg_rating'])  # Remove target column
    
    # Step 4: Scale the data
    X_hotel_scaled = scaler.transform(X_hotel)
    
    # Step 5: Make predictions
    predictions = model.predict(X_hotel_scaled)
    
    # Step 6: Calculate actual and predicted averages
    actual_avg_rating = hotel_data_rows['avg_rating'].mean()
    predicted_avg_rating = predictions.mean()

    # Step 7: Return the result
    return {
        "hotel_name": hotel_name,
        "hotel_id": hotel_id,
        "predicted_avg_rating": predicted_avg_rating,
        "actual_avg_rating": actual_avg_rating,
        "num_reviews": len(hotel_data_rows),
        "sample_data": hotel_data_rows.head(1).to_dict(orient='records')[0]
    }


def main():
    # S3 bucket details
    s3_bucket = 'andorra-hotels-data-warehouse'
    
    # Prefixes
    nlp_prefix = 'model_training/nlp/'
    hotel_map_prefix = 'model_training/validation/'
    model_prefix = 'model_training/supervised/'
    scaler_prefix = 'model_training/validation/'

    # Model input from user
    model_name_input = "random_forest"

    # Get the latest NLP Parquet file
    nlp_file_key = get_latest_file(s3_bucket, nlp_prefix, 'nlp', '.parquet')
    df = load_file_from_s3(s3_bucket, nlp_file_key, 'parquet')

    # Get the latest hotel_id_mapping CSV file
    hotel_map_file_key = get_latest_file(s3_bucket, hotel_map_prefix, 'hotel_id_name_mapping', '.csv')
    hotel_map = load_file_from_s3(s3_bucket, hotel_map_file_key, 'csv')

    # Get the latest model file based on user input
    model_file_key = get_latest_file(s3_bucket, model_prefix, f'model_{model_name_input}', '.pkl')
    model = load_model_from_s3(s3_bucket, model_file_key)

    # Get the latest scaler file
    scaler_file_key = get_latest_file(s3_bucket, scaler_prefix, 'scaler', '.pkl')
    scaler = load_model_from_s3(s3_bucket, scaler_file_key)

    # Predict hotel rating
    hotel_name_input = "Hotel NH Collection Andorra Palomé"
    result = predict_hotel_rating(hotel_name_input, hotel_map, df, model, scaler)

    # Display the result
    if isinstance(result, dict):
        print(f"Hotel Name: {result['hotel_name']}")
        print(f"Hotel ID: {result['hotel_id']}")
        print(f"Predicted Avg Rating: {result['predicted_avg_rating']}")
        print(f"Actual Avg Rating: {result['actual_avg_rating']}")
        print(f"Number of Reviews: {result['num_reviews']}")
        print(f"Sample Data: {result['sample_data']}")
    else:
        print(result)


if __name__ == "__main__":
    main()