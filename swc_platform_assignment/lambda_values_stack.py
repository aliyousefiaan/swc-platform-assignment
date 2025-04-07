from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_iam as iam,
    aws_lambda as lambda_,
    custom_resources as cr,
    aws_ec2 as ec2,
    Duration,
    CustomResource,
    BundlingOptions,
    DockerImage
)
from constructs import Construct

class LambdaValuesStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        parameter_name = config["parameter_name"]

        # Create a Lambda layer for the dependencies
        lambda_values_dependencies_layer = lambda_.LayerVersion(
            self,
            "LambdaValuesDependenciesLayer",
            code=lambda_.Code.from_asset(
                "swc_platform_assignment/lambda_values/dependencies_layer",
                bundling=BundlingOptions(
                    image=DockerImage.from_registry("registry.hub.docker.com/library/python:3.13"),
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output/python"
                    ]
                )
            ),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_13],
        )
        # Create Lambda function for generating values
        lambda_values_lambda = lambda_.Function(
            self,
            "LambdaValuesGenerator",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="lambda_values.lambda_handler",
            code=lambda_.Code.from_asset("swc_platform_assignment/lambda_values"),
            timeout=Duration.seconds(10),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            layers=[lambda_values_dependencies_layer]
        )
        # Add SSM permissions to Lambda
        lambda_values_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "ssm:GetParameters", "ssm:DescribeParameters"],
                resources=[f"arn:aws:ssm:{self.region}:{self.account}:parameter{parameter_name}"]
            )
        )

        self.values = CustomResource(
            self,
            "LambdaValues",
            service_token=lambda_values_lambda.function_arn,
            properties={
                "ParameterName": parameter_name,
            }
        )
