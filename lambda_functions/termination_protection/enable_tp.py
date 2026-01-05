import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    client = boto3.client('ec2')
except Exception as e:
    logger.exception({
        "incident_id": incident_id,
        "step": "enable_termination_protection",
        "instance_id": instance_id,
        "error": str(e)
    })
    raise

def main(instance_id,incident_id):
    try:
        response = client.modify_instance_attribute(InstanceId=instance_id, DisableApiTermination={
        'Value': True
        })
    except Exception as e:
        logger.exception({
        "incident_id": incident_id,
        "step": "enable_termination_protection",
        "instance_id": instance_id,
        "message": "Error occurred when trying to disable termination protection for the EC2 instance.",
        "error": str(e)
    })
    #raise

    


#if __name__ == '__main__':
instance_id = ''
incident_id = ''
main(instance_id,incident_id)