from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_ec2 as _ec2,
    aws_rds as _rds,
    aws_lambda as _lambda,
    aws_ssm as _ssm,
    aws_apigateway as _api
)
from constructs import Construct

class RdsEc2BastionStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        vpc = _ec2.Vpc(self, 'VPC', max_azs=2, nat_gateways=1, #TODO only have 1 nat gateway in dev, default for prod
                                subnet_configuration= [_ec2.SubnetConfiguration(name='private_with_egress',
                                                            cidr_mask=24,
                                                        subnet_type=_ec2.SubnetType.PRIVATE_WITH_EGRESS
                                                        ),
                                                        _ec2.SubnetConfiguration(name='public',
                                                        cidr_mask=24,
                                                        subnet_type=_ec2.SubnetType.PUBLIC
                                                        ),
                                                        _ec2.SubnetConfiguration(name='private_only',
                                                        cidr_mask=24,
                                                        subnet_type=_ec2.SubnetType.PRIVATE_ISOLATED
                                                        )                                               
                                ]
        )

        ec2_sg = _ec2.SecurityGroup(self, 'bastion-host-sg', vpc=vpc
                                    )
        ec2_sg.add_ingress_rule(_ec2.Peer.any_ipv4(), _ec2.Port.tcp(22))

        ec2 = _ec2.Instance(self, 'bastion-host',
                            instance_type= _ec2.InstanceType('t2.micro'),
                            machine_image=_ec2.AmazonLinuxImage(
                                generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
                                ),
                            vpc= vpc,
                            vpc_subnets= _ec2.SubnetSelection(
                                subnet_type= _ec2.SubnetType.PUBLIC,
                                ),
                            security_group= ec2_sg
        )
        rds_sg = _ec2.SecurityGroup(self, 'rds-sg', vpc=vpc
                                    )
        # rds_sg.add_ingress_rule(_ec2.Peer.ipv4(ec2.instance_private_ip), _ec2.Port.tcp(3306))
        rds = _rds.DatabaseCluster(self, 'bastion-database',
            engine=_rds.DatabaseClusterEngine.aurora_mysql(version=_rds.AuroraMysqlEngineVersion.VER_3_02_1),
            credentials=_rds.Credentials.from_generated_secret("clusteradmin"),  # Optional - will default to 'admin' username and generated password
            instance_props=_rds.InstanceProps(
                vpc=vpc,
                vpc_subnets=_ec2.SubnetSelection(
                    subnet_type= _ec2.SubnetType.PRIVATE_ISOLATED
                    ),
                security_groups=[rds_sg],
                ),
            default_database_name= 'db',
            port=3306,
            instances=1
        )
        _ssm.StringParameter(self, 'db-info', string_value= rds.secret.secret_name ,parameter_name='db-secret-name')

        #give RDS inbound allowance to the security group of the ec2 instance (traffic over private IP)
        rds_sg.connections.allow_from(ec2, _ec2.Port.tcp(3306))
        #When you specify a security group as the source or destination for a rule, the rule affects all instances that are associated with the security groups. 
        #The instances can communicate in the specified direction, using the PRIVATE IP addresses of the instances, over the specified protocol and port.
        # https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html]

        lambda_sg = _ec2.SecurityGroup(self, 'lambda-sg', vpc=vpc)
        rds.connections.allow_from(lambda_sg, _ec2.Port.tcp(3306))
        #create a lambda layer with pymysql installed
        lambda_layer = _lambda.LayerVersion(self, 'lambda-layer',
            code=_lambda.Code.from_asset('lambda/layer'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
            description='A layer to pymysql'
        )
        secrets_interface_endpoint = _ec2.InterfaceVpcEndpoint(self, 'secrets-interface-endpoint', vpc=vpc, 
                                                        service = _ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
                                                        security_groups=[lambda_sg],
                                                        subnets=_ec2.SubnetSelection(
                                                            subnet_type= _ec2.SubnetType.PRIVATE_WITH_EGRESS
                                                        )
        )
        #lambda to connect to RDS
        lambda_func = _lambda.Function(self, 'lambda-function',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda'),
            handler='lambda_function.lambda_handler',
            layers=[lambda_layer],
            vpc=vpc,
            vpc_subnets=_ec2.SubnetSelection(
                subnet_type= _ec2.SubnetType.PRIVATE_ISOLATED
                ),
            security_groups=[lambda_sg],
            environment={
                'DB_SECRET_NAME': rds.secret.secret_name
            }
        )
        #grant lambda access to secrets manager
        rds.secret.grant_read(lambda_func)

        db_api = _api.LambdaRestApi(self, 'db-api',
            handler=lambda_func,
            proxy=True,
                # deploy_options={
                #     "logging_level": _api.MethodLoggingLevel.INFO,
                #     "data_trace_enabled": True,
                #     "throttling_burst_limit": 100,
                #     "throttling_rate_limit": 100,
                #     "metrics_enabled": True
                # },
            endpoint_types=[_api.EndpointType.REGIONAL],
            deploy=True,

            default_cors_preflight_options=_api.CorsOptions(
                allow_origins=_api.Cors.ALL_ORIGINS,
                allow_methods=_api.Cors.ALL_METHODS,
                allow_headers= ['*']
            ),
            deploy_options=_api.StageOptions(stage_name='test')
        )

                                    