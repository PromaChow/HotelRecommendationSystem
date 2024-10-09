import boto3
import sys

# Initialize the Boto3 clients for Lambda and ECR
lambda_client = boto3.client('lambda')
ecr_client = boto3.client('ecr')

LAMBDA_FUNCTION_NAME = 'model_inference_lambda'
ECR_REPOSITORY_NAME = 'lambda-docker'
AWS_REGION = 'us-west-2'

def get_repository_uri():
    try:
        # Get the repository URI using describe_repositories
        response = ecr_client.describe_repositories(
            repositoryNames=[ECR_REPOSITORY_NAME]
        )
        repository_uri = response['repositories'][0]['repositoryUri']
        return repository_uri
    except Exception as e:
        print(f'Error getting repository URI from ECR: {str(e)}')
        sys.exit(1)

def get_latest_image_uri():
    try:
        # Get all images from ECR and sort them by 'imagePushedAt'
        response = ecr_client.describe_images(
            repositoryName=ECR_REPOSITORY_NAME,
            maxResults=1000  # Adjust as needed if you have many images
        )
        
        # Ensure we have images and sort them by imagePushedAt
        images = response.get('imageDetails', [])
        if not images:
            print("No images found in the repository.")
            sys.exit(1)

        # Sort images by the timestamp when they were pushed (newest first)
        latest_image = max(images, key=lambda x: x['imagePushedAt'])

        # Get the image URI using the latest image digest and repository URI
        latest_image_digest = latest_image['imageDigest']
        repository_uri = get_repository_uri()
        latest_image_uri = f'{repository_uri}@{latest_image_digest}'

        print(f'Latest ECR image URI: {latest_image_uri}')
        return latest_image_uri

    except Exception as e:
        print(f'Error getting latest image URI from ECR: {str(e)}')
        sys.exit(1)

def get_lambda_image_uri():
    try:
        # Get the current image URI used by the Lambda function (use get_function instead of get_function_configuration)
        response = lambda_client.get_function(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        # The ImageUri will be in the Code section of the response
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