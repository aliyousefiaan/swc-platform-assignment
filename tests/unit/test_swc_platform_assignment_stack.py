import aws_cdk as core
import aws_cdk.assertions as assertions

from swc_platform_assignment.swc_platform_assignment_stack import SwcPlatformAssignmentStack

# example tests. To run these tests, uncomment this file along with the example
# resource in swc_platform_assignment/swc_platform_assignment_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SwcPlatformAssignmentStack(app, "swc-platform-assignment")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
