import pandas as pd
import os
import pickle
import boto3
from botocore.exceptions import NoCredentialsError
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime
import math

def get_latest_parquet_file_path(s3_bucket, input_prefix):
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=input_prefix)
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in S3 bucket: {s3_bucket} with prefix: {input_prefix}")
        
        parquet_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.parquet')]
        if not parquet_files:
            raise FileNotFoundError(f"No Parquet files found in the specified S3 bucket.")
        
        latest_file = max(parquet_files, key=lambda x: x['LastModified'])
        return f"s3://{s3_bucket}/{latest_file['Key']}"
    
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found.")

def load_data(parquet_file_path):
    df = pd.read_parquet(parquet_file_path)
    return df

def save_model_to_s3(local_file_path, s3_bucket, output_prefix, current_datetime, model_type):
    output_file_name = f"model_{model_type}_{current_datetime}.pkl"
    final_output_path = f"{output_prefix}{output_file_name}"
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.upload_file(local_file_path, s3_bucket, final_output_path)
    os.remove(local_file_path)

def save_scaler_to_s3(scaler, s3_bucket, validation_prefix, current_datetime):
    # Save the scaler locally first
    local_scaler_path = f"/tmp/scaler_{current_datetime}.pkl"
    
    with open(local_scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    # Define the S3 path and upload the scaler
    output_file_name = f"scaler_{current_datetime}.pkl"
    final_output_path = f"{validation_prefix}{output_file_name}"
    
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.upload_file(local_scaler_path, s3_bucket, final_output_path)
    
    # Remove the local scaler file
    os.remove(local_scaler_path)
    
    print(f"Scaler saved to S3 as {final_output_path}")

def save_results_to_s3(df, s3_bucket, output_prefix, current_datetime, file_format='parquet'):
    local_temp_path = f"/tmp/training_results_{current_datetime}.parquet"
    df.to_parquet(local_temp_path, engine='pyarrow', index=False)
    output_file_name = f"training_results_{current_datetime}.parquet"
    final_output_path = f"{output_prefix}{output_file_name}"
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.upload_file(local_temp_path, s3_bucket, final_output_path)
    os.remove(local_temp_path)
    print(f"Results saved to S3 as {final_output_path}")

def preprocess_data(df):
    X = df.drop(columns=['avg_rating'])  # Features
    y = df['avg_rating']  # Target
    return X, y

def scale_data(X_train, X_test, s3_bucket, validation_prefix, current_datetime):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save the scaler to S3
    save_scaler_to_s3(scaler, s3_bucket, validation_prefix, current_datetime)
    
    return X_train_scaled, X_test_scaled

def adjusted_r_squared(r2, n, p):
    return 1 - (1 - r2) * ((n - 1) / (n - p - 1))

def train_and_evaluate_models_with_tuning(X_train, X_test, y_train, y_test, s3_bucket, output_prefix, model_save_path='models'):
    models = {
        'Random Forest': (RandomForestRegressor(random_state=42), {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 20],
            'min_samples_split': [5, 10],
            'min_samples_leaf': [2, 4],
            'max_features': ['sqrt', 0.5],  # Regularization to reduce overfitting
        }),
        'Gradient Boosting': (GradientBoostingRegressor(random_state=42), {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1],
            'max_depth': [3, 5],
            'min_samples_split': [5, 10],
            'min_samples_leaf': [2, 4],
            'subsample': [0.8, 1.0],
            'max_features': ['sqrt', 0.5],  # Regularization to prevent overfitting
            'n_iter_no_change': [10],  # Early stopping
            'validation_fraction': [0.2]  # Early stopping validation
        }),
        'Support Vector Machine': (SVR(), {
            'kernel': ['linear', 'rbf'],
            'C': [0.1, 1, 10],
            'epsilon': [0.1, 0.2, 0.5]
        }),
        'Neural Network': (MLPRegressor(random_state=42, max_iter=500, early_stopping=True), {
            'hidden_layer_sizes': [(50,), (100,), (50, 50)],
            'activation': ['relu', 'tanh'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate_init': [0.001, 0.01]
        })
    }

    results = []  
    n = len(y_test)
    p = X_train.shape[1]  

    if not os.path.exists(model_save_path):
        os.makedirs(model_save_path)

    for name, (model, param_grid) in models.items():
        print(f"Tuning {name}...")

        randomized_search = RandomizedSearchCV(model, param_distributions=param_grid, 
                                               n_iter=20, cv=5, scoring='neg_mean_squared_error', n_jobs=-1, random_state=42)
        randomized_search.fit(X_train, y_train)
        
        best_model = randomized_search.best_estimator_
        y_pred = best_model.predict(X_test)
        
        rmse = math.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        adj_r2 = adjusted_r_squared(r2, n, p)

        results.append({
            'Model': name,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'Adjusted R2': adj_r2,
            'Best Params': randomized_search.best_params_
        })
        
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_save_path}/model_{name.replace(' ', '_').lower()}_{current_date}.pkl"
        
        with open(model_filename, 'wb') as file:
            pickle.dump(best_model, file)
        
        save_model_to_s3(model_filename, s3_bucket, output_prefix, current_date, name.replace(' ', '_').lower())
        print(f"Model {name} saved with best params: {randomized_search.best_params_}")
    
    results_df = pd.DataFrame(results)
    print(results_df)
    
    return results_df

def main():
    s3_bucket = 'andorra-hotels-data-warehouse'
    input_prefix = 'model_training/nlp/'
    output_prefix = 'model_training/supervised/'
    validation_prefix = 'model_training/validation/'
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    parquet_file_path = get_latest_parquet_file_path(s3_bucket, input_prefix)
    df = load_data(parquet_file_path)

    X, y = preprocess_data(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the data and save the scaler to S3
    X_train_scaled, X_test_scaled = scale_data(X_train, X_test, s3_bucket, validation_prefix, current_datetime)

    results_df = train_and_evaluate_models_with_tuning(X_train_scaled, X_test_scaled, y_train, y_test, s3_bucket, output_prefix, model_save_path='/tmp')

    save_results_to_s3(results_df, s3_bucket, output_prefix, current_datetime, file_format='parquet')


if __name__ == "__main__":
    main()