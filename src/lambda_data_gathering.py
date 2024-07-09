import json
import boto3
import requests
from datetime import datetime
from secrets_manager import get_parameter

s3 = boto3.client('s3')

def get_hotels_in_region(region, API_KEY):
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query=hotels+in+{region}&key={API_KEY}'
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json().get('results', [])

def get_hotel_details(place_id, API_KEY):
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}'
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json().get('result', {})

def extract_hotel_data(hotel, API_KEY, NUM_REVIEWS):
    details = get_hotel_details(hotel['place_id'], API_KEY)
    return {
        "hotel_name": details.get('name', ''),
        "location": details.get('vicinity', ''),
        "max_number_of_people": 2,
        "address": details.get('formatted_address', ''),
        "price_per_night": None,
        "amenities": {amenity: True for amenity in details.get('amenities', [])},
        "images": [photo['photo_reference'] for photo in details.get('photos', [])],
        "reviews": [
            {
                "user": review.get('author_name', ''),
                "rating": review.get('rating', 0),
                "date": review.get('relative_time_description', ''),
                "review": review.get('text', '')
            } for review in details.get('reviews', [])[:NUM_REVIEWS]
        ],
        "source": f"https://maps.googleapis.com/maps/api/place/details/json?place_id={hotel['place_id']}&key={API_KEY}"
    }

def lambda_handler(event, context=None):
    # Retrieve secrets from AWS Systems Manager Parameter Store
    GOOGLE_PLACES_API_KEY = get_parameter('GOOGLE_PLACES_API_KEY')

    NUM_HOTELS = event['num_hotels']
    NUM_REVIEWS = event["num_reviews"]
    region = event['region']

    hotels = get_hotels_in_region(region, GOOGLE_PLACES_API_KEY)
    
    hotel_details = []
    for hotel in hotels[:NUM_HOTELS]:
        hotel_data = extract_hotel_data(hotel, GOOGLE_PLACES_API_KEY, NUM_REVIEWS)
        hotel_details.append(hotel_data)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_name = f'raw_data/{region}_{current_date}.json'
    
    s3.put_object(
        Bucket='andorra-hotels-data-warehouse',
        Key=file_name,
        Body=json.dumps(hotel_details, indent=4)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data retrieved and stored in S3')
    }

# Main function to trigger the lambda_handler
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

        response = lambda_handler(event)
        print(response)

if __name__ == '__main__':
    main()