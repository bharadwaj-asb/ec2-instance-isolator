import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Function to remove from ELB v2
def elb2(instance_id, target_group_arn,incident_id):
    try:
        client = boto3.client('elbv2')
    except Exception as e:
        print(f' {e}')
        logger.exception({
        "incident_id": incident_id,
        "step": "deregister_elb",
        "instance_id": instance_id,
        "message":"Exception occurred when creating auto-scaling client",
        "error": str(e)
    })
    #raise



    try:
        response = client.deregister_targets(
            TargetGroupArn = target_group_arn,
            Targets=[
                {
                    'Id': instance_id
                }
                ]
            )
        logger.info(
        {
            "step": "deregister_elb",
            "function": "elbv2",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully deregistered instance: {instance_id} from ELB v2"
            })

    except Exception as e:
        logger.exception({
        "incident_id": incident_id,
        "step": "deregister_elb",
        "instance_id": instance_id,
        "message":"Exception occurred when deregistering instance from elbv2:",
        "error": str(e)
    }) 
        #raise



def lambda_handler(event, context):
    instance_id = event['InstanceId']
    elb_name = event['ELBNames']
    incident_id = event['IncidentId']
    target_group_arn = event['TargetGroups']
    elb2(instance_id, target_group_arn,incident_id)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully deregistering ELB')
    }
