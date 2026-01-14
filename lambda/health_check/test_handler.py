import json
import os
import sys
from unittest.mock import Mock, patch


os.environ['DYNAMODB_TABLE'] = 'test-requests-db'


def test_health_check_success():
    """Test successful health check request processing."""
    mock_table = Mock()
    mock_table.put_item = Mock(
        return_value={'ResponseMetadata': {'HTTPStatusCode': 200}}
    )

    mock_dynamodb = Mock()
    mock_dynamodb.Table = Mock(return_value=mock_table)

    with patch('boto3.resource', return_value=mock_dynamodb):
        if 'index' in sys.modules:
            del sys.modules['index']
        from index import lambda_handler
  
        event = {
            'httpMethod': 'GET',
            'path': '/health',
            'headers': {'User-Agent': 'pytest/1.0'},
            'requestContext': {'identity': {'sourceIp': '127.0.0.1'}}
        }

        context = Mock()
        response = lambda_handler(event, context)

        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'application/json'

        body = json.loads(response['body'])
        assert body['status'] == 'healthy'
        assert body['message'] == 'Request processed and saved.'
        assert 'requestId' in body


def test_health_check_post_request():
    """Test health check handles POST requests."""
    mock_table = Mock()
    mock_table.put_item = Mock(
        return_value={'ResponseMetadata': {'HTTPStatusCode': 200}}
    )

    mock_dynamodb = Mock()
    mock_dynamodb.Table = Mock(return_value=mock_table)

    with patch('boto3.resource', return_value=mock_dynamodb):
        if 'index' in sys.modules:
            del sys.modules['index']
        from index import lambda_handler

        event = {
            'httpMethod': 'POST',
            'path': '/health',
            'headers': {'User-Agent': 'pytest/1.0'},
            'requestContext': {'identity': {'sourceIp': '192.168.1.1'}}
        }

        context = Mock()
        response = lambda_handler(event, context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'healthy'


def test_health_check_dynamodb_failure():
    """Test Lambda handles DynamoDB errors gracefully."""
    mock_table = Mock()
    mock_table.put_item = Mock(side_effect=Exception('DynamoDB unavailable'))

    mock_dynamodb = Mock()
    mock_dynamodb.Table = Mock(return_value=mock_table)

    with patch('boto3.resource', return_value=mock_dynamodb):
        if 'index' in sys.modules:
            del sys.modules['index']
        from index import lambda_handler

        event = {
            'httpMethod': 'GET',
            'path': '/health',
            'headers': {},
            'requestContext': {'identity': {'sourceIp': '127.0.0.1'}}
        }

        context = Mock()
        response = lambda_handler(event, context)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['status'] == 'unhealthy'
        assert body['message'] == 'Failed to save request'


if __name__ == '__main__':
    """Run tests directly without pytest."""
    tests = [
        test_health_check_success,
        test_health_check_post_request,
        test_health_check_dynamodb_failure
    ]

    print("Running health check Lambda tests...")
    print("=" * 60)

    for test in tests:
        test()
        print(f"✅ {test.__name__} PASSED")

    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
