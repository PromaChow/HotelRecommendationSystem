import boto3

def get_parameter(name):
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=name,
        WithDecryption=True
    )
    return response['Parameter']['Value']


# Name of the parameter to retrieve
parameter_name = 'GOOGLE_PLACES_API_KEY'

# Retrieve the parameter
api_key = get_parameter(parameter_name)

# Print the retrieved API key
print(f"The API key is: {api_key}")