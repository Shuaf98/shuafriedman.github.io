from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as _s3,
    RemovalPolicy,
    aws_route53 as _route53,
    aws_certificatemanager as _acm,
    aws_cloudfront as _cloudfront,
    aws_cloudfront_origins as _origins,
    aws_wafv2 as _waf,
    aws_lambda as _lambda,
    # aws_lambda as _lambda,
    aws_ssm as _ssm,
    aws_iam as _iam,
    # aws_apigateway as _api,
    aws_route53_targets as _targets,
    Duration,
    RemovalPolicy,    
)
from constructs import Construct
import json
import subprocess

class CloudfrontWebDistributionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the command to be executed
        domain = ''
        subdomain = ''
        siteDomain = f'{subdomain}.{domain}'
        hosted_zone = _route53.HostedZone.from_lookup(self, f'{subdomain}-zone', domain_name = domain)
        # certificate = _acm.Certificate(
        #     self, f'{subdomain}-cert',
        #     domain_name=f'*.{domain}',
        #     validation=_acm.CertificateValidation.from_dns(hosted_zone)
        # )
        certificate_arn = _ssm.StringParameter.value_for_string_parameter(self,f'certificate')
        certificate = _acm.Certificate.from_certificate_arn(self, f'cert', 
                                                            certificate_arn=certificate_arn)

        _bucket = _s3.Bucket(self, f'{siteDomain}',
                        # website_index_document="index.html",
                        # public_read_access=True,
                        block_public_access=_s3.BlockPublicAccess.BLOCK_ACLS,
                        removal_policy=RemovalPolicy.DESTROY,
                        auto_delete_objects=True
                    )

        cfResponseHeadersPolicy =  _cloudfront.ResponseHeadersPolicy(self, 'cfResponseHeadersPolicy', 
                                    response_headers_policy_name= 'lambdaFurlCloudFrontPolicy',
                                    cors_behavior = _cloudfront.ResponseHeadersCorsBehavior(
                                                    access_control_allow_credentials = False,
                                                    access_control_allow_headers =['*'],
                                                    access_control_allow_methods= ["GET","HEAD","OPTIONS","PUT","PATCH","POST","DELETE"],
                                                    access_control_allow_origins= ['*'],
                                                    access_control_expose_headers= ['*'],
                                                    access_control_max_age= Duration.seconds(500),
                                                    origin_override= True
                                    )                                                                
        )
        cf_ = _cloudfront.Distribution(self, f'{subdomain}-distribution',
            default_behavior=_cloudfront.BehaviorOptions(
                origin=_origins.S3Origin(_bucket),
                allowed_methods = _cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy= _cloudfront.CachePolicy.CACHING_DISABLED, #CACHING_OPTIMIZED,
                viewer_protocol_policy=_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                response_headers_policy= cfResponseHeadersPolicy,
                origin_request_policy = _cloudfront.OriginRequestPolicy.CORS_CUSTOM_ORIGIN
            ),
            domain_names=[siteDomain],
            certificate=certificate,
            default_root_object="index.html",
        )
            # geo_restriction= _cloudfront.GeoRestriction.allowlist("US", "CA", "IL",
            # price_class= _cloudfront.PriceClass.PRICE_CLASS_100
            # default_root_object="index.html",
            # error_configurations=[
            #     _cloudfront.CfnDistribution.CustomErrorResponseProperty(
            #         error_code=404,
            #         response_code=200,
            #         response_page_path="/index.html"
            #     )
            # ],

        _route53.ARecord(self, f'{subdomain}-Arecord', record_name=subdomain, zone=hosted_zone, 
                         target=_route53.RecordTarget.from_alias(_targets.CloudFrontTarget(cf_)))

