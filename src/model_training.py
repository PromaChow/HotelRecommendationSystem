import os
import numpy as np
import pandas as pd
import ast
import torch
import torch.nn as nn
import torch.optim as optim
import boto3
from sklearn.model_selection import train_test_split

class SimpleNN(nn.Module):
    def __init__(self, input_dim):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x

def extract_features(text_features):
    if isinstance(text_features, str):
        try:
            features_dict = ast.literal_eval(text_features)
        except ValueError:
            raise ValueError(f"Cannot parse the string: {text_features}")
    elif isinstance(text_features, dict):
        features_dict = text_features
    else:
        raise ValueError(f"Unexpected data type: {type(text_features)}")
    
    feature_type = features_dict.get('type', None)
    size = features_dict.get('size', None)
    indices = features_dict.get('indices', [])
    values = features_dict.get('values', [])
    
    if isinstance(indices, np.ndarray):
        indices = indices.tolist()
    if isinstance(values, np.ndarray):
        values = values.tolist()
    
    return feature_type, size, indices, values

def download_data_from_s3(bucket_name, s3_key, local_file_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_file_path)
    print(f"Downloaded {s3_key} from S3 bucket {bucket_name} to {local_file_path}")

def upload_model_to_s3(bucket_name, s3_key, local_model_path):
    s3 = boto3.client('s3')
    s3.upload_file(local_model_path, bucket_name, s3_key)
    print(f"Uploaded model to S3 bucket {bucket_name} at {s3_key}")

def main():
    # S3 details
    bucket_name = 'andorra-hotels-data-warehouse'
    s3_data_key = 'l3_data/text/l2_data_2024-08-21_08-11-52.parquet'
    s3_model_key = f'models/simple_nn_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.pth'
    local_data_path = 'model/local_data.parquet'
    local_model_path = 'model/hotel_recom_model.pth'

    # Download data from S3
    download_data_from_s3(bucket_name, s3_data_key, local_data_path)

    # Load the dataset
    df = pd.read_parquet(local_data_path)
    
    # Apply the function to extract type, size, indices, and values
    df['type'], df['size'], df['indices'], df['values'] = zip(*df['review_text_features'].apply(extract_features))

    # Convert boolean columns to integers (1 or 0)
    df = df.copy()
    bool_columns = df.select_dtypes(include=['bool']).columns
    df[bool_columns] = df[bool_columns].astype(int)

    # Expand indices into separate columns
    max_len_indices = df['indices'].apply(len).max()
    max_len_values = df['values'].apply(len).max()

    for i in range(max_len_indices):
        df[f'index_{i}'] = df['indices'].apply(lambda x: x[i] if i < len(x) else 0)

    for i in range(max_len_values):
        df[f'value_{i}'] = df['values'].apply(lambda x: x[i] if i < len(x) else 0)

    # Drop the original 'indices' and 'values' columns
    df = df.drop(['indices', 'values'], axis=1)

    # Convert all numerical data to float32 and handle any object type issues
    df = df.apply(pd.to_numeric, errors='coerce')

    # Replace NaN with 0 or another placeholder if necessary
    df = df.fillna(0)

    # Convert to tensors
    X = df.drop('avg_rating', axis=1).values
    y = df['avg_rating'].values

    # Splitting data into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Convert data to PyTorch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)

    input_dim = X_train.shape[1]
    model = SimpleNN(input_dim)

    # Loss and optimizer
    criterion = nn.MSELoss()  # Assuming a regression problem
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    num_epochs = 20
    for epoch in range(num_epochs):
        model.train()
        outputs = model(X_train)
        loss = criterion(outputs, y_train.unsqueeze(1))  # unsqueeze to match output dimensions
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

    # Evaluating the model
    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test)
        test_loss = criterion(test_outputs, y_test.unsqueeze(1))
        print(f'Test Loss: {test_loss.item():.4f}')

    # Save the model locally
    torch.save(model.state_dict(), local_model_path)
    print(f"Model saved locally at {local_model_path}")

    # Upload the model to S3
    upload_model_to_s3(bucket_name, s3_model_key, local_model_path)

if __name__ == "__main__":
    main()