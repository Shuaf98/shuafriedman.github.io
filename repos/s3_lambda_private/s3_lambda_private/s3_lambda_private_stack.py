from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_ec2 as _ec2,
    aws_s3 as _s3,
    aws_lambda as _lambda,
    RemovalPolicy
)
from constructs import Construct

class S3LambdaPrivateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # I want this code in python
        vpc = _ec2.Vpc(self, 's3-lambda-vpc', max_azs=2, 
                        subnet_configuration= [
                                                _ec2.SubnetConfiguration(name='private_only',
                                                                        cidr_mask=24,
                                                                         subnet_type=_ec2.SubnetType.PRIVATE_ISOLATED
                                                                         ),
                        ]
                        )
        vpc.add_gateway_endpoint('test-endpoint', service= _ec2.GatewayVpcEndpointAwsService.S3, subnets=[_ec2.SubnetSelection(subnet_type=_ec2.SubnetType.PRIVATE_ISOLATED)])
        bucket = _s3.Bucket(self, 'test_s3_bucket',
                            bucket_name='test-private-bucket-access',
                            auto_delete_objects= True,
                            removal_policy= RemovalPolicy.DESTROY
                            )
        s3_lambda = _lambda.Function(
            self, 'testprivate-lambda', 
            code = _lambda.Code.from_asset('lambda'),
            runtime = _lambda.Runtime.PYTHON_3_8,
            handler = 'handler.lambda_handler',
            environment= {'BUCKET': bucket.bucket_name},
            vpc=vpc,
            vpc_subnets= _ec2.SubnetSelection(
                    subnet_type=_ec2.SubnetType.PRIVATE_ISOLATED,
                ),
        )
        bucket.grant_read_write(s3_lambda)
        bucket.grant_public_access()