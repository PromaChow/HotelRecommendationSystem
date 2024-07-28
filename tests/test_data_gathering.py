# coverage run -m pytest -q tests/test_data_gathering.py
# coverage report --show-missing --include=data_gathering.py --omit=/tests/

import pytest
from src.secrets_manager import get_parameter
from src.data_gathering import (
    get_hotels_in_region, 
    get_hotel_details, 
    get_photo_url, 
    download_photo, 
    upload_to_s3, 
    extract_and_download_photos, 
    extract_hotel_data, 
    get_raw_data, 
    get_serpapi_reviews,
    main
    )

API_KEY = get_parameter('GOOGLE_PLACES_API_KEY')
SERPAPI_KEY = get_parameter('SERAPI_API_KEY')
PHOTO_REFERENCE = "AUc7tXXhEGi2Hlczu2QkT_zwLTcNQ8eXESzlwEJN8e6vhbpXn7xXhBKbl2mikhStLYRnHRDhke11Lk5rAZJPKcNH7HzIX0En5vpctCTFkhs_5pj3n90obm7BjkA1A2-ZDU_Ny7HmQEU_qGMQ4xowhyaz9NoEyLv1ReVMP7q-XaEI2iF2Jx1g"
BUCKET_NAME = "andorra-hotels-data-warehouse"

def test_get_hotels_in_region():
    region = 'Andorra la Vella'

    response = get_hotels_in_region(region, API_KEY)
    assert response

def test_get_hotels_in_region_next_page_token():
    region = 'Andorra la Vella'
    api_key = API_KEY

    response = get_hotels_in_region(region, api_key)
    next_page_token = response.get('next_page_token')

    response = get_hotels_in_region(region, api_key, next_page_token)
    assert response

def test_get_hotel_details():
    place_id = "ChIJVVQbRJv0pRIRz_P-C-3PTcs"
    response = get_hotel_details(place_id, API_KEY)
    assert response

def test_get_serpapi_reviews():
    place_id = "ChIJVVQbRJv0pRIRz_P-C-3PTcs"
    reviews = get_serpapi_reviews(place_id, SERPAPI_KEY, 2)
    assert isinstance(reviews, list)
    assert isinstance(reviews[0], dict)
    assert len(reviews) == 2

def test_get_serpapi_reviews_error():
    place_id = "sthrandom-C-3PTcs"
    reviews = get_serpapi_reviews(place_id, SERPAPI_KEY, 2)
    assert [] == reviews

def test_photo_url():
    url = get_photo_url(PHOTO_REFERENCE, API_KEY)
    assert url.startswith("https://maps.googleapis.com/maps/api/place/photo?")

def test_download_photo():
    url = get_photo_url(PHOTO_REFERENCE, API_KEY)
    response = download_photo(url)
    assert response

def test_wrong_photo():
    wrong_photo_reference = "sth"
    url = get_photo_url(wrong_photo_reference, API_KEY)
    response = download_photo(url)
    assert response is None

def test_upload_to_s3():
    url = get_photo_url(PHOTO_REFERENCE, API_KEY)
    file_content = download_photo(url)
    s3_path = "tests/example.jpg"
    s3_url = upload_to_s3(file_content, BUCKET_NAME, s3_path)
    assert s3_url

def test_extract_and_download_photos():
    place_id = "ChIJVVQbRJv0pRIRz_P-C-3PTcs"
    details = get_hotel_details(place_id, API_KEY)
    region = "Andorra la Vella"
    info = extract_and_download_photos(details, API_KEY, BUCKET_NAME, region)
    assert info

def test_extract_hotel_data():
    place_id = "ChIJVVQbRJv0pRIRz_P-C-3PTcs"
    details = get_hotel_details(place_id, API_KEY)
    region = "Andorra la Vella"
    extract_hotel_data(details, API_KEY, SERPAPI_KEY, 1, BUCKET_NAME, region)

def test_get_raw_data():
    # I AM NOT GOING TO TEST THE MAIN FUNCION SINCE ITS TESTED WITH THE DATA GATHERING GA
    pass

def test_main():
    # I AM NOT GOING TO TEST THE MAIN FUNCION SINCE ITS TESTED WITH THE DATA GATHERING GA
    pass
