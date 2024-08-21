import os
import subprocess
import sys

# Install dependencies from requirements.txt
# subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Rest of your training code...
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
import os
import pandas as pd

def main():
    # Define the directory where SageMaker will download the data
    input_dir = f'input/data/training'

    # Load the dataset
    data = pd.read_parquet(os.path.join(input_dir, 'l2_data_2024-08-02_06-12-06.parquet'))
    
    # Example data preprocessing
    X_train = np.random.rand(1000, 10)
    y_train = np.random.rand(1000, 1)

    # Assuming the last column is the target and the rest are features
    # X_train = data.iloc[:, :-1].values
    # y_train = data.iloc[:, -1].values

    # Hyperparameters passed by SageMaker
    batch_size = int(os.getenv('batch_size', 32))
    learning_rate = float(os.getenv('learning_rate', 0.01))

    # Model definition
    model = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dense(64, activation='relu'),
        Dense(1, activation='linear')
    ])

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                  loss='mean_squared_error')

    model.fit(X_train, y_train, epochs=10, batch_size=batch_size)

    # Save the model to the location SageMaker expects
    model_dir = f'model'
    model.save(os.path.join(model_dir, 'hotel_recom_model'))

if __name__ == "__main__":
    main()