import pandas as pd
import pickle
import boto3
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

        files = [obj for obj in response['Contents'] if obj['Key'].startswith(f"{prefix}{starts_with}") and obj['Key'].endswith(ends_with)]
        if not files:
            raise FileNotFoundError(f"No files found starting with {starts_with} and ending with {ends_with} in {s3_bucket}")

        latest_file = max(files, key=lambda x: x['LastModified'])
        return latest_file['Key']  # Return just the S3 key
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found. Please configure your credentials.")


def load_file_from_s3(s3_bucket, file_key, file_type='parquet'):
    """
    Load a file (Parquet/CSV) from S3 into a DataFrame.
    """
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
    hotel_id = get_hotel_id_from_name(hotel_name, hotel_map)
    if hotel_id is None:
        return f"No hotel found with the name: {hotel_name}"
    
    hotel_data_rows = val_data[val_data['hotel_id'] == hotel_id]
    if hotel_data_rows.empty:
        return f"No data found for hotel ID: {hotel_id}"
    
    X_hotel = hotel_data_rows.drop(columns=['avg_rating'])  # Remove target column
    X_hotel_scaled = scaler.transform(X_hotel)
    predictions = model.predict(X_hotel_scaled)
    
    actual_avg_rating = hotel_data_rows['avg_rating'].mean()
    predicted_avg_rating = predictions.mean()

    return {
        "hotel_name": hotel_name,
        "hotel_id": int(hotel_id), 
        "predicted_avg_rating": float(predicted_avg_rating), 
        "actual_avg_rating": float(actual_avg_rating), 
        "num_reviews": int(len(hotel_data_rows)), 
        "sample_data": hotel_data_rows.head(1).to_dict(orient='records')[0]
    }


def lambda_handler(event, context):
    """
    Lambda handler function to process the input event and return hotel rating predictions.
    """
    try:
        # S3 bucket details
        s3_bucket = 'andorra-hotels-data-warehouse'
        
        # Prefixes
        nlp_prefix = 'model_training/nlp/'
        hotel_map_prefix = 'model_training/validation/'
        model_prefix = 'model_training/supervised/'
        scaler_prefix = 'model_training/validation/'

        hotel_name_input = event.get('hotel_name', "Hotel NH Collection Andorra Palomé")
        model_name_input = event.get('model_name', "random_forest")

        nlp_file_key = get_latest_file(s3_bucket, nlp_prefix, 'nlp', '.parquet')
        df = load_file_from_s3(s3_bucket, nlp_file_key, 'parquet')

        hotel_map_file_key = get_latest_file(s3_bucket, hotel_map_prefix, 'hotel_id_name_mapping', '.csv')
        hotel_map = load_file_from_s3(s3_bucket, hotel_map_file_key, 'csv')

        model_file_key = get_latest_file(s3_bucket, model_prefix, f'model_{model_name_input}', '.pkl')
        model = load_model_from_s3(s3_bucket, model_file_key)

        scaler_file_key = get_latest_file(s3_bucket, scaler_prefix, 'scaler', '.pkl')
        scaler = load_model_from_s3(s3_bucket, scaler_file_key)

        result = predict_hotel_rating(hotel_name_input, hotel_map, df, model, scaler)

        return {
            "statusCode": 200,
            "body": result
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error processing request: {str(e)}"
        }