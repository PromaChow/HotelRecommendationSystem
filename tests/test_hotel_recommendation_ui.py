# coverage run -m pytest -q tests/test_hotel_recommendation_ui.py
# coverage report --show-missing --include=dhotel_recommendation_ui.py --omit=/tests/

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import boto3
from moto import mock_aws
from io import BytesIO
from src.hotel_recommendations_ui import get_hotels_by_region, display_hotel_images, call_api

# Constants for tests
S3_BUCKET = 'andorra-hotels-data-warehouse'
CURRENT_DATETIME = '2024-10-2_12-00-00'
PREFIX = 'model_training/validation/'
STARTS_WITH = 'hotel_id_name_mapping'
ENDS_WITH = '.csv'

@pytest.fixture
def hotel_map_data():
    return pd.DataFrame({
        'hotel_id': [1, 2, 3],
        'hotel_name': ['Hotel A', 'Hotel B', 'Hotel C'],
        'region': ['Andorra la Vella', 'Canillo', 'Encamp']
    })

### Test: get_hotels_by_region
def test_get_hotels_by_region(hotel_map_data):
    region = 'Andorra la Vella'
    filtered_hotels = get_hotels_by_region(region, hotel_map_data)
    
    # Check that only hotels from 'Andorra la Vella' are returned
    assert len(filtered_hotels) == 1
    assert filtered_hotels.iloc[0]['hotel_name'] == 'Hotel A'

### Test: display_hotel_images
@mock_aws
@patch('streamlit.image')
def test_display_hotel_images(mock_st_image):
    # Set up the mock S3 environment
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(Bucket=S3_BUCKET, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
    
    # Add mock images to the S3 bucket
    s3.put_object(Bucket=S3_BUCKET, Key="raw_data/images/Andorra la Vella/Hotel A/image1.jpg", Body=b"image-data")
    
    # Test the function
    display_hotel_images(S3_BUCKET, 'Andorra la Vella', 'Hotel A')
    
    # Check that streamlit.image was called
    assert mock_st_image.called

### Test: call_api
@patch('requests.post')
def test_call_api(mock_post, hotel_map_data):
    # Set up mock API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hotel_name": "Novotel Andorra",
        "predicted_avg_rating": 4.5
    }
    mock_post.return_value = mock_response
    
    # Filter the data to get the hotel_name
    hotel_name = 'Novotel Andorra'
    model_name = 'random_forest'
    region = 'Andorra la Vella'
    
    filtered_hotels = get_hotels_by_region(region, hotel_map_data)
    api_response = call_api(hotel_name, model_name, region)
    
    # Check that the API was called correctly and the response is as expected
    assert api_response['hotel_name'] == 'Novotel Andorra'
    assert api_response['predicted_avg_rating'] == 4.5
    mock_post.assert_called_once()