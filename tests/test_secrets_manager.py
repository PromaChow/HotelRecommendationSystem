# coverage run -m pytest -q tests/test_secrets_manager.py
# coverage report --show-missing --include=secrets_manager.py --omit=/tests/

import pytest
from src.secrets_manager import get_parameter

def test_get_parameter():
    parameter_name = 'GOOGLE_PLACES_API_KEY'

    # Retrieve the parameter
    api_key = get_parameter(parameter_name)

    # Print the retrieved API key
    print(f"The API key is: {api_key}")
    
    assert isinstance(api_key, str)