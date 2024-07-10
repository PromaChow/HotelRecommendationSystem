from src.data_gathering import lambda_handler


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