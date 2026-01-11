import boto3
from datetime import datetime
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(client,instance_id,incident_id):
    try:
        response = client.create_tags(
            Resources=[instance_id],
            Tags=[
                    {
                        'Key': 'IncidentStatus',
                        'Value': 'Quarantined'
                    },
                    {
                        'Key': 'QuarantineTime',
                        'Value': str(datetime.now())
                    },
                    {
                        'Key': 'IncidentId',
                        'Value': incident_id
                    }

            ])
        logger.info(
            {
            "step": "tag_quarantined_instance",
            "function": "main",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully added tags for quarantined instance"
            })

    except Exception as e:
        logger.exception({
        "incident_id": incident_id,
        "step": "tag_quarantined_instance",
        "instance_id": instance_id,
        "message":"Exception occurred when tagging the instance.",
        "error": str(e)
    })


    



def lambda_handler(event, context):
    instance_id = event['InstanceId']
    incident_id=event['IncidentId']
    try:
        client = boto3.client('ec2')
    except Exception as e:
        logger.exception({
        "incident_id": incident_id,
        "step": "ebs_snapshots",
        "instance_id": instance_id,
        "message":"Exception occurred when creating EC2 client.",
        "error": str(e)
    })
        raise

    main(client,instance_id,incident_id)
    return {
        **event,
        'statusCode': 200,
        'body': json.dumps('Successfully tagged the quarantined instance')
    }
