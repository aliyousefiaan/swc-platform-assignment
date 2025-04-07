import boto3
import cfnresponse
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        request_type = event['RequestType']

        if request_type == 'Delete':
            logger.info("Delete request received")
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            return

        ssm = boto3.client('ssm')
        param_name = event['ResourceProperties']['ParameterName']
        logger.info(f"Getting SSM parameter: {param_name}")
        
        response = ssm.get_parameter(Name=param_name)
        environment = response['Parameter']['Value'].lower()
        logger.info(f"Environment value: {environment}")

        if environment == 'dev':
            replica_count = 1
        elif environment in ('staging', 'prod'):
            replica_count = 2
        else:
            raise ValueError(f"Unknown environment: {environment}")

        response_data = {
            "ReplicaCount": str(replica_count),
            "Environment": environment
        }
        logger.info(f"Sending response data: {json.dumps(response_data)}")

        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Message": str(e)})
