import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)



def main(client,instance_id, asg_name,incident_id):
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
 


def lambda_handler(event, context):
    instance_id = 'i-0485bd939bfd72eea'
    asg_name = event['ASGNames']
    incident_id = event['IncidentId']
    try:
        client = boto3.client('autoscaling')
    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "detach_asg",
                "function": "main",
                "instance_id": instance_id,
                "message":"Exception occurred when creating auto-scaling client",
                "error":str(e)
            })

    main(client,instance_id, asg_name, incident_id)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully detached EC2 instance from autoscaling group:')
    }
