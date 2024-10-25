# coverage run -m pytest -q tests/test_data_preprocessing_t3.py
# coverage report --show-missing --include=data_preprocessing_t3.py --omit=/tests/

import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import boto3
from moto import mock_aws
from src.data_preprocessing_t3 import save_hotel_id_name_mapping_to_csv, preprocess_data, save_to_s3

# Constants
S3_BUCKET = 'andorra-hotels-data-warehouse'
CURRENT_DATETIME = '2024-10-1_12-00-00'

@pytest.fixture
def l2_data():
    return pd.DataFrame({
        'region': ['Europe', 'Asia', 'Europe', 'Asia'],
        'hotel_name': ['Hotel A', 'Hotel B', 'Hotel A', 'Hotel C'],
        'review_language': ['en', 'es', 'fr', 'de'],
        'latitude': [45.0, 20.0, 45.1, 19.9],
        'longitude': [9.0, 10.0, 9.1, 10.1],
    })


@mock_aws
def test_save_hotel_id_name_mapping_to_csv(monkeypatch, l2_data):
    # Mock S3
    s3 = boto3.client('s3', region_name='us-west-2')
    # Specify LocationConstraint during bucket creation
    s3.create_bucket(Bucket=S3_BUCKET, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})

    # Mock the os.remove function
    mock_remove = MagicMock()
    monkeypatch.setattr(os, 'remove', mock_remove)

    # Mock the print function
    mock_print = MagicMock()
    monkeypatch.setattr('builtins.print', mock_print)

    # Run the function
    save_hotel_id_name_mapping_to_csv(l2_data, S3_BUCKET, CURRENT_DATETIME)

    # Check that the file was uploaded to S3
    s3_object_listing = s3.list_objects(Bucket=S3_BUCKET)
    assert len(s3_object_listing.get('Contents', [])) == 1

    # Check that the file was removed locally
    mock_remove.assert_called_once()

    # Check that print was called with correct output
    mock_print.assert_called_with(f"Hotel ID, Name and Region mapping saved to S3 as model_training/validation/hotel_id_name_mapping_{CURRENT_DATETIME}.csv")



def test_preprocess_data(l2_data):
    processed_data = preprocess_data(l2_data)

    # Ensure the hotel_id column is created
    assert 'hotel_id' in processed_data.columns

    # Ensure region and review_language are dropped
    assert 'region' not in processed_data.columns
    assert 'review_language' not in processed_data.columns
    assert 'hotel_name' not in processed_data.columns

    # Check if the encoded columns exist
    assert any(col.startswith('region_') for col in processed_data.columns)
    assert any(col.startswith('lang_') for col in processed_data.columns)


def test_save_to_s3():
    # I AM NOT GOING TO TEST THIS FUNCION SINCE ITS TESTED WITH THE DATA PREPROCESSING GA
    pass
