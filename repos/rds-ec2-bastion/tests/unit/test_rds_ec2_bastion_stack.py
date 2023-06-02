import aws_cdk as core
import aws_cdk.assertions as assertions

from rds_ec2_bastion.rds_ec2_bastion_stack import RdsEc2BastionStack

# example tests. To run these tests, uncomment this file along with the example
# resource in rds_ec2_bastion/rds_ec2_bastion_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RdsEc2BastionStack(app, "rds-ec2-bastion")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
