import json
import uuid
import os
from datetime import datetime, timezone
import boto3


dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_TABLE']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Health check endpoint that logs requests and stores them in DynamoDB
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    # Log the incoming request to CloudWatch
    print(f"Health check request received: {json.dumps(event)}")

    # Prepare item for DynamoDB
    item = {
        'id': request_id,
        'timestamp': timestamp,
        'method': event.get('httpMethod', 'UNKNOWN'),
        'path': event.get('path', '/health'),
        'sourceIp': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown'),
        'userAgent': event.get('headers', {}).get('User-Agent', 'unknown')
    }

    # Save to DynamoDB
    try:
        table.put_item(Item=item)
        print(f"Request saved to DynamoDB with ID: {request_id}")
    except Exception as e:
        print(f"Error saving to DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'unhealthy',
                'message': 'Failed to save request'
            })
        }

    # Return success response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'status': 'healthy',
            'message': 'Request processed and saved.',
            'requestId': request_id
        })
    }
