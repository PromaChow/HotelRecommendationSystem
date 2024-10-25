import streamlit as st
import requests
import boto3

from utils import get_latest_file, load_file_from_s3

# Function to filter hotels based on the region
def get_hotels_by_region(region, hotel_map):
    filtered_hotels = hotel_map[hotel_map['region'] == region]
    return filtered_hotels

# Function to retrieve and display images from S3 using signed URLs
def display_hotel_images(s3_bucket, region, hotel_name):
    s3 = boto3.client('s3')
    image_prefix = f"raw_data/images/{region}/{hotel_name}/"
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=image_prefix)
        if 'Contents' not in response:
            st.error(f"No images found for {hotel_name}")
            return

        # Display each image using Streamlit without caption and with fixed width
        for obj in response['Contents']:
            if obj['Key'].endswith(('.jpg', '.png')):
                image_url = s3.generate_presigned_url('get_object', Params={'Bucket': s3_bucket, 'Key': obj['Key']}, ExpiresIn=3600)
                st.image(image_url, width=300)  # Set a fixed width for the images
    except Exception as e:
        st.error(f"Error retrieving images from S3: {e}")

# Streamlit UI setup
st.title("Andorra Hotel Recommendations App")

# Model selection dropdown
model_name = st.selectbox(
    "Select Model Name",
    ["gradient_boosting", "neural_network", "random_forest", "support_vector_machine"]
)

# Region selection dropdown
andorra_region = st.selectbox(
    "Select Andorra Region",
    ["Andorra la Vella", "Canillo", "Encamp", "Escaldes-Engordany", "La Massana", "Ordino", "Sant Julià de Lòria"]
)

# S3 bucket details
s3_bucket = 'andorra-hotels-data-warehouse'
hotel_map_prefix = 'model_training/validation/'

# Load hotel data from S3
hotel_map_file_key = get_latest_file(s3_bucket, hotel_map_prefix, 'hotel_id_name_mapping', '.csv')
if hotel_map_file_key:
    hotel_map = load_file_from_s3(s3_bucket, hotel_map_file_key)

    # Filter hotels by the selected region
    if andorra_region:
        filtered_hotels = get_hotels_by_region(andorra_region, hotel_map)
        hotel_name = st.selectbox(
            "Select Hotel",
            filtered_hotels['hotel_name'] if not filtered_hotels.empty else ["No hotels available in this region"]
        )
else:
    st.error("Failed to load hotel data from S3.")

# API call function
def call_api(hotel_name, model_name, andorra_region):
    hotel_id = int(filtered_hotels[filtered_hotels['hotel_name'] == hotel_name]['hotel_id'].values[0])
    payload = {
        "hotel_name": hotel_name,
        "model_name": model_name,
        "andorra_region": andorra_region,
        "hotel_id": hotel_id
    }
    url = "https://vs2haothob.execute-api.us-west-2.amazonaws.com/prod/invoke"
    response = requests.post(url, json=payload)
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch data from the API"}

# Button to get recommendations and display images
if st.button("Get Recommendation"):
    if model_name and hotel_name and andorra_region:
        api_response = call_api(hotel_name, model_name, andorra_region)
        
        # Extract and display only the relevant fields: hotel_name, predicted_avg_rating
        if 'hotel_name' in api_response and 'predicted_avg_rating' in api_response:
            # Round predicted_avg_rating to 2 decimal places and mention it's out of 5
            rounded_predicted_rating = round(api_response['predicted_avg_rating'], 2)
            st.write(f"**Hotel Name**: {api_response['hotel_name']}")
            st.write(f"**Predicted Average Rating**: {rounded_predicted_rating} out of 5")
        else:
            st.error("API response does not contain the expected fields.")
        
        # Display hotel images
        st.write(f"**Displaying images for {hotel_name}:**")
        display_hotel_images(s3_bucket, andorra_region, hotel_name)
    else:
        st.error("Please fill in all inputs")