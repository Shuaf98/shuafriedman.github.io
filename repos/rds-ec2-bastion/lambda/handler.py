import json
import boto3
import pymysql
import os

def lambda_handler(event, context):
    # TODO implement
    #Get rds secret name from secrets manager  'db-secret-name', region = 'us-east-1'

    def get_secret_value(secret_name):
        region_name = "us-east-1" # replace with your region name
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"The requested secret {secret_name} was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                print(f"The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print(f"The request had invalid params:", e)
            else:
                print(f"Unexpected error: {e}")
        else:
            if 'SecretString' in response:
                return response['SecretString']
            else:
                return response['SecretBinary']
    
    secret_name = os.environ['DB_SECRET_NAME']
    secret = get_secret_value(secret_name)
    secret_dict = json.loads(secret)

    #connect to RDS
    import pymysql
    conn = pymysql.connect(
        host=secret_dict['host'],
        port=secret_dict['port'],
        user=secret_dict['username'],
        password=secret_dict['password'],
        db=secret_dict['dbname'],
        connect_timeout=5

    )
    cur = conn.cursor()
    if cur:
        print("Connection Successful")
        success = True
    else:
        print("Connection Unsuccessful")
        success = False
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'success': success
    }
    