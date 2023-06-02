#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cloudfront_web_distribution.cloudfront_web_distribution_stack import CloudfrontWebDistributionStack


app = cdk.App()
CloudfrontWebDistributionStack(app, "CloudfrontWebDistributionStack",

    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    )

app.synth()
