import aws_cdk as core
import aws_cdk.assertions as assertions

from sagemaker_studio_setup.sagemaker_studio_setup_stack import SagemakerStudioSetupStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sagemaker_studio_setup/sagemaker_studio_setup_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SagemakerStudioSetupStack(app, "sagemaker-studio-setup")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
