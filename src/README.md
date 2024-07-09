
# Data Gathering

To get a dataset which contained updated hotels and reviews of the Andorran region, and that it was maintained and updated frequently I decided to use the Google Places API. 

To do that we must follow the next steps: 

1. Set uo a Google Cloud Project 

    - Create a Google Cloud Project: Go to the Google Cloud Console and create a new project.
    - Enable Billing: Enable billing for your project, as the Places API is a paid service.

        To ensure that we are not going to surpass the 300$ budget we do the following computations
        - Places API: Text Search = 17$/100 requests and Details = 17$ per 1000 requests
        - Each request returns approx 20 results: (7 * 100) / 20 = 35 search requests per region. 35 * 7 regions = 245 search requests.
        - For 350 hotels we need 350 place details requests.
        - Total requests = 245 + 350 = 595 requests
        - Total cost 595 requests * 17$ / 1000 requests = 10.11$
        
        Hence, since Google Cloud you only pay per consumption, we should have enough money. 
    - Create a new Project with the dropdown called `AndorraHotelsDataCollection`.
    - Enable the Places API: Navigate to the API Library and enable the "Places API" for your project.

2. Get Your API Key

    - Create API Key: Go to the Credentials page and create an API key. This key will be used to authenticate your requests to the Google Places API.

3. Make API Requests

    - Find Hotels: Use the Place Search request to find hotels in a specific region.
    - Get Details: Use the Place Details request to get detailed information about each hotel, including reviews.

4. Define the Search requests

    - To search for hotels in a specific region (e.g., Andorra la Vella), you can use the following endpoint:
        ```bash
        https://maps.googleapis.com/maps/api/place/textsearch/json?query=hotels+in+Andorra+la+Vella&key=YOUR_API_KEY
        ```
    - To get detailed information about a specific hotel, including reviews, use the Place Details request:
        ```bash
        https://maps.googleapis.com/maps/api/place/details/json?place_id=PLACE_ID&key=YOUR_API_KEY
        ```

5. Define the dataset format: 
    ```json
    {
    "hotel_name": "Hotel Example",
    "location": "Andorra la Vella",
    "max_number_of_people": 2,
    "address": "123 Example Street, Andorra la Vella, Andorra",
    "price_per_night": 100,
    "features": {
      "wifi": true,
      "parking": true,
      "pool": false
    },
    "images": [
      "url1.jpg",
      "url2.jpg"
    ],
    "reviews": [
      {
        "user": "John Doe",
        "rating": 4.5,
        "date": "2023-05-01",
        "review": "Great place to stay!"
      },
      {
        "user": "John Doe",
        "rating": 4.5,
        "date": "2023-05-01",
        "review": "Great place to stay!"
      }
    ],
    "source": "Google Places API Link"
    }
    ```

6. Automate data gathering process: 
    - since we want to be able to automate the data refreshing, we will build an AWS Lambda Function to retrieve the hotel data from the Google Places API. 
    - Then, we will connect to AWS API Gateway to expose a REST API that triggers the Lambda Function
    - We will then finalize by storing the data into an S3 bucket. 

## Saving Secrets

To save secrets we wanted to use AWS Secrets manager but it does not have a free tier, hence we used the AWS Systems Manager Parameter Store, to use it we followed the next steps: 
1.	Go to the AWS Management Console.
2.	Navigate to “AWS Systems Manager” > "Parameter Store".
3.	Create 3 new parameters for your credentials:
    - Add your keys as key-value pairs
        ```json
        {
            "ADMIN_ACCESS_KEY_ID": "aws_access_key_id",
            "ADMIN_SECRET_ACCESS_KEY": "aws_secret_access_key",
            "GOOGLE_PLACES_API_KEY": "google_places_api_key"
        }
        ```
    - Select "Standard" tier and "Secure String"
4. A function called `get_secrets()` was created to retrieve that information.

5. For the GitHub Action, I stored the secrets into GitHub Secrets following the next steps:
    - Go to the Github repository in the website
    - Click on Settings > Secrets and Variables > Actions
    - Added the following secrets: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

## Lambda Process

Created the `lambda_data_gathering.py` file with the logic of the data gathering, we have to then package it and add it to the terraform folder using the following commands: 

- First create a dependencies folder and type the following command:
    ```bash
    pip install -r requirements.txt -t lambda/data_gathering/
    cp src/lambda_data_gathering.py lambda/data_gathering/
    cp src/secrets_manager.py lambda/data_gathering/
    ```

- Then package the lambda functionality into a zip file
    ```bash
    cd lambda/data_gathering/
    zip -r ../../tf/lambda_data_gathering.zip ./*
    ```

We then re-applied the terraform commands to apply the changes into out AWS account. 

To test the lambda process, we can go the the AWS Console, click on Lmabda > data_gathering_lambda > Test and test a single query: 
```json
{
  "region": "Andorra la Vella",
  "num_hotels": 1,
  "num_reviews": 1
}
```