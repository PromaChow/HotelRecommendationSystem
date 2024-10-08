import boto3
import sys

# Initialize the Boto3 clients for Lambda and ECR
lambda_client = boto3.client('lambda')
ecr_client = boto3.client('ecr')

LAMBDA_FUNCTION_NAME = 'model_inference_lambda'
ECR_REPOSITORY_NAME = 'lambda-docker'
AWS_REGION = 'us-west-2'

def get_latest_image_uri():
    try:
        # Get the latest image pushed to ECR
        response = ecr_client.describe_images(
            repositoryName=ECR_REPOSITORY_NAME,
            filter={'tagStatus': 'TAGGED'},
            maxResults=1,
            sortBy='TIMESTAMP'
        )
        latest_image = response['imageDetails'][0]
        latest_image_digest = latest_image['imageDigest']
        latest_image_uri = f'{response["repositoryUri"]}@{latest_image_digest}'

        print(f'Latest ECR image URI: {latest_image_uri}')
        return latest_image_uri
    except Exception as e:
        print(f'Error getting latest image URI from ECR: {str(e)}')
        sys.exit(1)

def get_lambda_image_uri():
    try:
        # Get the current image URI used by the Lambda function
        response = lambda_client.get_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        current_image_uri = response['Code']['ImageUri']
        print(f'Current Lambda image URI: {current_image_uri}')
        return current_image_uri
    except Exception as e:
        print(f'Error getting Lambda image URI: {str(e)}')
        sys.exit(1)

def update_lambda_image_uri(new_image_uri):
    try:
        # Update the Lambda function with the new image URI
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ImageUri=new_image_uri
        )
        print(f'Lambda function updated to use image: {new_image_uri}')
        return response
    except Exception as e:
        print(f'Error updating Lambda function: {str(e)}')
        sys.exit(1)

def check_and_update_image():
    latest_image_uri = get_latest_image_uri()
    current_lambda_image_uri = get_lambda_image_uri()

    if latest_image_uri == current_lambda_image_uri:
        print('Lambda function is already using the latest image.')
    else:
        print('Lambda function is not using the latest image. Updating...')
        update_lambda_image_uri(latest_image_uri)

if __name__ == '__main__':
    check_and_update_image()