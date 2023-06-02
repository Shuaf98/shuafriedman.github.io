import aws_cdk as core
import aws_cdk.assertions as assertions

from summarization_endpoint.summarization_endpoint_stack import SummarizationEndpointStack

# example tests. To run these tests, uncomment this file along with the example
# resource in summarization_endpoint/summarization_endpoint_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SummarizationEndpointStack(app, "summarization-endpoint")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
