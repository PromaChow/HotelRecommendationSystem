import json
import boto3
import requests
import time
from datetime import datetime
from secrets_manager import get_parameter
from urllib.parse import urlencode

s3 = boto3.client('s3', region_name='us-west-2')

def get_hotels_in_region(region, API_KEY, next_page_token=None):
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query=hotels+in+{region}&key={API_KEY}'
    if next_page_token:
        url += f'&pagetoken={next_page_token}'
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()

def get_hotel_details(place_id, API_KEY):
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}'
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json().get('result', {})

def get_photo_url(photo_reference, api_key, max_width=400):
    params = {
        'maxwidth': max_width,
        'photoreference': photo_reference,
        'key': api_key
    }
    url = f"https://maps.googleapis.com/maps/api/place/photo?{urlencode(params)}"
    return url

def download_photo(photo_url):
    response = requests.get(photo_url, allow_redirects=True)
    if response.status_code == 200:
        return response.content
    return None

def upload_to_s3(file_content, bucket_name, s3_path):
    s3.put_object(Bucket=bucket_name, Key=s3_path, Body=file_content)
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_path}"
    return s3_url

def extract_and_download_photos(hotel, api_key, bucket_name, region):
    photos_info = []
    hotel_name = hotel.get('name', '')
    for photo in hotel.get('photos', []):
        photo_reference = photo.get('photo_reference')
        if photo_reference:
            photo_url = get_photo_url(photo_reference, api_key)
            photo_content = download_photo(photo_url)
            if photo_content:
                photo_filename = f"{hotel['place_id']}_{photo_reference}.jpg"
                s3_path = f"raw_data/images/{region}/{hotel_name}/{photo_filename}"
                s3_url = upload_to_s3(photo_content, bucket_name, s3_path)
                photos_info.append({
                    "photo_reference": photo_reference,
                    "s3_url": s3_url,
                    "html_attributions": photo.get('html_attributions', [])
                })
    return photos_info

def extract_hotel_data(hotel, API_KEY, NUM_REVIEWS, bucket_name, region):
    details = get_hotel_details(hotel['place_id'], API_KEY)
    photos_info = extract_and_download_photos(details, API_KEY, bucket_name, region)
    
    # Sort reviews by date and select the latest 100 reviews
    sorted_reviews = sorted(details.get('reviews', []), key=lambda x: x.get('time', 0), reverse=True)[:NUM_REVIEWS]

    return {
        "hotel_name": details.get('name', ''),
        "location": details.get('vicinity', ''),
        "rating": hotel.get('rating', None),
        "user_ratings_total": hotel.get('user_ratings_total', 0),
        "max_number_of_people": 2,
        "address": details.get('formatted_address', ''),
        "business_status": hotel.get('business_status', ''),
        "place_id": hotel.get('place_id', ''),
        "amenities": {},  # You can update this based on available data
        "photos": photos_info,
        "reviews": [
            {
                "user": review.get('author_name', ''),
                "rating": review.get('rating', 0),
                "date": review.get('relative_time_description', ''),
                "review": review.get('text', '')
            } for review in sorted_reviews
        ],
        "source": f"https://maps.googleapis.com/maps/api/place/details/json?place_id={hotel['place_id']}&key={API_KEY}"
    }

def get_raw_data(event):
    # Retrieve secrets from AWS Systems Manager Parameter Store
    GOOGLE_PLACES_API_KEY = get_parameter('GOOGLE_PLACES_API_KEY')

    NUM_HOTELS = event['num_hotels']
    NUM_REVIEWS = event["num_reviews"]
    region = event['region']

    all_hotels = []
    next_page_token = None
    while len(all_hotels) < NUM_HOTELS:
        result = get_hotels_in_region(region, GOOGLE_PLACES_API_KEY, next_page_token)
        all_hotels.extend(result.get('results', []))
        next_page_token = result.get('next_page_token')
        if not next_page_token:
            break
        time.sleep(2)  # Sleep to comply with API rate limits

    hotel_details = []
    for hotel in all_hotels[:NUM_HOTELS]:
        hotel_data = extract_hotel_data(hotel, GOOGLE_PLACES_API_KEY, NUM_REVIEWS, 'andorra-hotels-data-warehouse', region)
        hotel_details.append(hotel_data)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_name = f'raw_data/text/{region}_{current_date}.json'
    
    s3.put_object(
        Bucket='andorra-hotels-data-warehouse',
        Key=file_name,
        Body=json.dumps(hotel_details, indent=4)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data retrieved and stored in S3')
    }

# Main function to trigger the get_raw_data function
def main():
    REGIONS = ['Andorra la Vella', 'Escaldes-Engordany', 'Encamp', 'Canillo', 'La Massana', 'Ordino', 'Sant Julià de Lòria']
    NUM_HOTELS = 50
    NUM_REVIEWS = 100

    for region in REGIONS:
        event = {
            'region': region, 
            'num_hotels': NUM_HOTELS,
            'num_reviews': NUM_REVIEWS
        }

        response = get_raw_data(event)
        print(response)

if __name__ == '__main__':
    main()