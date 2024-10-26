# coverage run -m pytest -q tests/test_model_deploy_tests.py
# coverage report --show-missing --include=model_deploy_tests.py --omit=/tests/


import pytest

from src.model_deploy_tests import get_lambda_image_uri, get_latest_image_uri, get_repository_uri, check_and_update_image

def test_get_repository_uri():
    uri = get_repository_uri()
    assert "lambda-docker" in uri

def test_get_latest_image_uri():
    latest_uri = get_latest_image_uri()
    assert "lambda-docker@sha256:" in latest_uri

def test_get_lambda_image_uri():
    latest_lambda_uri = get_lambda_image_uri()
    assert "lambda-docker@sha256:" in latest_lambda_uri

def test_update_lambda_image_uri():
    pass

def test_check_and_update_image():
    check_and_update_image()