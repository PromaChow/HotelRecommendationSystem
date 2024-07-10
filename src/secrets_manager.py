import boto3

def get_parameter(name):
    """
    Retrieves the value of an AWS Systems Manager (SSM) parameter.

    This function uses the Boto3 library to create a client for the AWS Systems Manager (SSM)
    service, and fetches the value of a specified parameter. It supports decryption of secure
    parameters.

    Parameters:
    name (str): The name of the parameter to retrieve.

    Returns:
    str: The decrypted value of the specified parameter.
    """
    ssm = boto3.client('ssm', region_name='us-west-2')
    response = ssm.get_parameter(
        Name=name,
        WithDecryption=True
    )
    return response['Parameter']['Value']