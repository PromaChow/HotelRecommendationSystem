import pandas as pd
import os
import pickle
import boto3
from botocore.exceptions import NoCredentialsError
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime
import math

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
    df = pd.read_parquet(parquet_file_path)
    return df

def save_model_to_s3(local_file_path, s3_bucket, output_prefix, current_datetime, model_type):
    """
    Save the model to S3 using boto3.
    """
    # Define the S3 output file name and path
    output_file_name = f"model_{model_type}_{current_datetime}.pkl"
    final_output_path = f"{output_prefix}{output_file_name}"

    # Upload the local model file to S3
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.upload_file(local_file_path, s3_bucket, final_output_path)

    # Remove the local temporary file after upload
    os.remove(local_file_path)

def save_results_to_s3(df, s3_bucket, output_prefix, current_datetime, file_format='parquet'):
    """
    Save the results DataFrame to S3 as a Parquet file using boto3.
    """
    # Define the local temporary file path
    local_temp_path = f"/tmp/training_results_{current_datetime}.parquet"
    df.to_parquet(local_temp_path, engine='pyarrow', index=False)

    # Define the S3 output file name and path
    output_file_name = f"training_results_{current_datetime}.parquet"
    final_output_path = f"{output_prefix}{output_file_name}"

    # Upload the local results file to S3
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.upload_file(local_temp_path, s3_bucket, final_output_path)

    # Remove the local temporary file after upload
    os.remove(local_temp_path)
    print(f"Results saved to S3 as {final_output_path}")

def preprocess_data(df):
    # Drop non-numeric features that are not required for training
    df = df.drop(columns=['hotel_id'])  # Example of dropping non-informative features

    # Define the label (target) and the features
    X = df.drop(columns=['avg_rating'])  # Features (all except avg_rating)
    y = df['avg_rating']  # Label

    return X, y

def split_data(X, y, test_size=0.2, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    return X_train, X_test, y_train, y_test

def scale_data(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled

def adjusted_r_squared(r2, n, p):
    """Calculate Adjusted R-Squared"""
    return 1 - (1 - r2) * ((n - 1) / (n - p - 1))

def train_and_evaluate_models_with_tuning(X_train, X_test, y_train, y_test, s3_bucket, output_prefix, model_save_path='models'):
    models = {
        'Random Forest': (RandomForestRegressor(random_state=42), {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }),
        'Gradient Boosting': (GradientBoostingRegressor(random_state=42), {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 10],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }),
        'Support Vector Machine': (SVR(), {
            'kernel': ['linear', 'rbf'],
            'C': [0.1, 1, 10],
            'epsilon': [0.1, 0.2, 0.5]
        }),
        'Neural Network': (MLPRegressor(random_state=42, max_iter=500), {
            'hidden_layer_sizes': [(50,), (100,), (50, 50)],
            'activation': ['relu', 'tanh'],
            'solver': ['adam', 'sgd'],
            'learning_rate_init': [0.001, 0.01]
        })
    }
    
    results = []  # To store results as a list of dictionaries
    
    n = len(y_test)  # Number of samples
    p = X_train.shape[1]  # Number of features

    # Create local directory for saving models
    if not os.path.exists(model_save_path):
        os.makedirs(model_save_path)

    for name, (model, param_grid) in models.items():
        print(f"Tuning {name}...")

        # Use RandomizedSearchCV for hyperparameter tuning (limited to 20 combinations)
        randomized_search = RandomizedSearchCV(model, param_distributions=param_grid, 
                                               n_iter=20, cv=3, scoring='neg_mean_squared_error', n_jobs=-1, random_state=42)
        randomized_search.fit(X_train, y_train)
        
        # Get the best estimator (model) from RandomizedSearch
        best_model = randomized_search.best_estimator_
        y_pred = best_model.predict(X_test)
        
        # Calculate metrics
        rmse = math.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        adj_r2 = adjusted_r_squared(r2, n, p)
        
        # Append results to the list as a dictionary
        results.append({
            'Model': name,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'Adjusted R2': adj_r2,
            'Best Params': randomized_search.best_params_  # Save the best parameters
        })
        
        # Save the model locally
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_save_path}/model_{name.replace(' ', '_').lower()}_{current_date}.pkl"
        
        with open(model_filename, 'wb') as file:
            pickle.dump(best_model, file)
        
        # Save the model to S3
        save_model_to_s3(model_filename, s3_bucket, output_prefix, current_date, name.replace(' ', '_').lower())
        print(f"Model {name} saved locally as {model_filename} and uploaded to S3 with best params: {randomized_search.best_params_}")
    
    # Convert the list of results into a DataFrame
    results_df = pd.DataFrame(results)
    
    # Print the results DataFrame
    print(results_df)
    
    return results_df


def main():
    # S3 bucket details
    s3_bucket = 'andorra-hotels-data-warehouse'
    input_prefix = 'model_training/nlp/'
    output_prefix = 'model_training/supervised/'
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Get the Parquet file path from S3
    parquet_file_path = get_latest_parquet_file_path(s3_bucket, input_prefix)
    print(parquet_file_path)

    # Load dataset
    df = load_data(parquet_file_path)

    # Preprocess data
    X, y = preprocess_data(df)

    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Scale data
    X_train_scaled, X_test_scaled = scale_data(X_train, X_test)

    # Train and evaluate models and save them to S3
    results_df = train_and_evaluate_models_with_tuning(X_train_scaled, X_test_scaled, y_train, y_test, s3_bucket, output_prefix, model_save_path='/tmp')

    # Save results DataFrame to S3 as a Parquet file
    save_results_to_s3(results_df, s3_bucket, output_prefix, current_datetime, file_format='parquet')

if __name__ == "__main__":
    main()