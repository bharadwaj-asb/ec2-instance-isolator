import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(instance_id,incident_id,client):
    try:
        response = client.modify_instance_attribute(InstanceId=instance_id, DisableApiTermination={
        'Value': True
        })
        logger.info(
             {
                  "step": "enable_tp",
                  "function": "main",
                  "incident_id": incident_id,
                  "message": f"Enabled termination protection for instance: {instance_id}"
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

def lambda_handler(event, context):
    
    instance_id = event['InstanceId']
    incident_id = event['IncidentId']
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

    main(instance_id,incident_id,client)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully enabled termination protection')
    }
