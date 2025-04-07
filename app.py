#!/usr/bin/env python3
import os
import json
import aws_cdk as cdk

from swc_platform_assignment.ssm_stack import SsmStack
from swc_platform_assignment.vpc_stack import VpcStack
from swc_platform_assignment.lambda_values_stack import LambdaValuesStack
from swc_platform_assignment.eks_stack import EksStack

def load_config(env_name: str) -> dict:
    config_path = os.path.join("config", f"{env_name}.json")
    with open(config_path, "r") as config_file:
        return json.load(config_file)

app = cdk.App()

env_name = app.node.try_get_context("env") or os.getenv("CDK_ENV", "dev")
config = load_config(env_name)

aws_env = cdk.Environment(region=config["region"])

# Create account environment SSM parameter
account_env_parameter = SsmStack(app, "account-env-parameter", env=aws_env, config=config)

# Create main VPC
vpc_main = VpcStack(app, "vpc-main", env=aws_env, config=config)

# Create Lambda values generator stack
lambda_values = LambdaValuesStack(app, "lambda-values", env=aws_env, vpc=vpc_main.vpc, config=config)

# Create main EKS cluster
eks_main = EksStack(app, "eks-main", env=aws_env, vpc=vpc_main.vpc, values=lambda_values.values, config=config)

app.synth()
