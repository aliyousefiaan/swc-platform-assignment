from aws_cdk import (
    Stack,
    aws_ssm as ssm
)
from constructs import Construct
from swc_platform_assignment.helpers.tags import common_tags

class SsmStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create env SSM parameter
        self.env_parameter = ssm.StringParameter(
            self,
            construct_id,
            parameter_name=config["parameter_name"],
            string_value=config["environment"],
        )

        common_tags(self.env_parameter, config)
