# coverage run -m pytest -q tests/test_supervised_training.py
# coverage report --show-missing --include=supervised_training.py --omit=/tests/

import pytest

from src.supervised_training import preprocess_data, scale_data, adjusted_r_squared

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from src.supervised_training import preprocess_data, scale_data, adjusted_r_squared

def test_preprocess_data():
    # Create a sample DataFrame with feature columns and a target column
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'feature2': [5, 6, 7, 8],
        'avg_rating': [3.5, 4.0, 4.5, 5.0]  # This is the target column
    })

    # Apply preprocessing
    X, y = preprocess_data(df)

    # Verify that `X` contains only the feature columns and `y` contains only the target
    assert list(X.columns) == ['feature1', 'feature2']
    assert y.equals(df['avg_rating'])


@patch("src.supervised_training.save_scaler_to_s3")
def test_scale_data(mock_save_scaler_to_s3):
    # Create sample training and testing data
    X_train = pd.DataFrame({'feature1': [1, 2, 3], 'feature2': [4, 5, 6]})
    X_test = pd.DataFrame({'feature1': [2, 3, 4], 'feature2': [5, 6, 7]})
    
    # Expected bucket and prefix values
    s3_bucket = "test-bucket"
    validation_prefix = "test-prefix"
    current_datetime = "2024-10-11_10-00-00"

    # Apply scaling
    X_train_scaled, X_test_scaled = scale_data(X_train, X_test, s3_bucket, validation_prefix, current_datetime)

    # Verify the scaling transformation (using sklearn's StandardScaler for comparison)
    scaler = StandardScaler()
    expected_train_scaled = scaler.fit_transform(X_train)
    expected_test_scaled = scaler.transform(X_test)

    # Compare scaled results
    np.testing.assert_almost_equal(X_train_scaled, expected_train_scaled)
    np.testing.assert_almost_equal(X_test_scaled, expected_test_scaled)

    # Ensure save_scaler_to_s3 was called with correct arguments
    mock_save_scaler_to_s3.assert_called_once_with(mock_save_scaler_to_s3.call_args[0][0], s3_bucket, validation_prefix, current_datetime)


def test_adjusted_r_squared():
    # Sample R-squared, number of samples, and number of predictors
    r2 = 0.85
    n = 100  # Total samples
    p = 5    # Predictors/features

    # Calculate adjusted R-squared manually
    expected_adj_r2 = 1 - (1 - r2) * ((n - 1) / (n - p - 1))

    # Use the function to calculate adjusted R-squared
    adj_r2 = adjusted_r_squared(r2, n, p)

    # Compare results
    assert adj_r2 == pytest.approx(expected_adj_r2, 0.01)