import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    client = boto3.client('autoscaling')
except Exception as e:
    print(f'Exception occurred when creating auto-scaling client: {e}')


def main(instance_id, asg_name,incident_id):
    try:
        response = client.detach_instances(
        InstanceIds=[instance_id],
        AutoScalingGroupName = asg_name,
        ShouldDecrementDesiredCapacity=False
        )
        logger.info(
        {
            "step": "detach_asg",
            "function": "main",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully detached EC2 instance from autoscaling group: {asg_name}"
            })


    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "detach_asg",
                "function": "main",
                "instance_id": instance_id,
                "message":"Exception occurred when detaching auto-scaling the the instance:",
                "error":str(e)
            })
 


#if __name__ == '__main__':
instance_id = 'i-0485bd939bfd72eea'
asg_name = 'test-asg'
incident_id = ''
main(instance_id, asg_name, incident_id)