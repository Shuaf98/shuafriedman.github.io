#!/usr/bin/env python3
import os

import aws_cdk as cdk

from summarization_endpoint.summarization_endpoint_stack import SummarizationEndpointStack


app = cdk.App()

SummarizationEndpointStack(app, "SummarizationEndpointStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()
