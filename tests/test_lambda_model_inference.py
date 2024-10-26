# coverage run -m pytest -q tests/test_lambda_model_inference.py
# coverage report --show-missing --include=lambda_model_inference.py --omit=/tests/
import pytest

from src.lambda_model_inference import lambda_handler

def test_main_lambda_handler():
    event = {
        "hotel_name": "Hotel Sol Park",
        "model_name": "random_forest"
    }
    prediction = lambda_handler(event, {})
    print(prediction)
    assert prediction is not None


def test_api_example():
    event_api = {
        "version": "2.0",
        "routeKey": "POST /invoke",
        "rawPath": "/prod/invoke",
        "rawQueryString": "",
        "headers": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "content-length": "69",
        "content-type": "application/json",
        "host": "vs2haothob.execute-api.us-west-2.amazonaws.com",
        "postman-token": "0b07bf00-2162-4c8a-909c-cd679b8c6a10",
        "user-agent": "PostmanRuntime/7.36.1",
        "x-amzn-trace-id": "Root=1-670a1721-5b1fb432231ced4f3e79fd46",
        "x-forwarded-for": "88.159.85.252",
        "x-forwarded-port": "443",
        "x-forwarded-proto": "https"
        },
        "requestContext": {
        "accountId": "590183875407",
        "apiId": "vs2haothob",
        "domainName": "vs2haothob.execute-api.us-west-2.amazonaws.com",
        "domainPrefix": "vs2haothob",
        "http": {
        "method": "POST",
        "path": "/prod/invoke",
        "protocol": "HTTP/1.1",
        "sourceIp": "88.159.85.252",
        "userAgent": "PostmanRuntime/7.36.1"
        },
        "requestId": "fhiNNi4YvHcESGw=",
        "routeKey": "POST /invoke",
        "stage": "prod",
        "time": "12/Oct/2024:06:28:49 +0000",
        "timeEpoch": 1728714529069
        },
        "body": "{\n  \"hotel_name\": \"Hotel Sol Park\",\n  \"model_name\": \"random_forest\"\n}",
        "isBase64Encoded": False
    }

    prediction = lambda_handler(event_api, {})
    assert prediction is not None

def test_error_request_body():
    event = {
        "body": "sth random"
    }
    prediction = lambda_handler(event, {})
    assert prediction["statusCode"] == 400