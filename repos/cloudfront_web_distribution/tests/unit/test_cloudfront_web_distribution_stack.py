import aws_cdk as core
import aws_cdk.assertions as assertions

from cloudfront_web_distribution.cloudfront_web_distribution_stack import CloudfrontWebDistributionStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cloudfront_web_distribution/cloudfront_web_distribution_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CloudfrontWebDistributionStack(app, "cloudfront-web-distribution")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
