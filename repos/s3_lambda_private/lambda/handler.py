import json
import boto3
import os

def lambda_handler(event, context):
    # TODO implement
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('test.txt', os.environ['BUCKET'], 'test.txt')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }