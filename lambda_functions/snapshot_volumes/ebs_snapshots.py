import boto3
from datetime import datetime
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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


# Function to create snapshot and encrypt it
def main(vols,instance_id,incident_id): 
        for each_vol in vols:
            try:
                response = client.create_snapshot(
                    Description= 'This is a snapshot of a quarantined EBS volume',
                    VolumeId= each_vol,
                    TagSpecifications=[
                        {
                             'ResourceType': 'snapshot',
                            'Tags': [
                                {
                                    'Key': 'IncidentStatus',
                                    'Value': 'Quarantined'
                                },
                                {
                                    'Key': 'QuarantineTime',
                                    'Value': str(datetime.now())
                                }
                            ]
                        }
                    ]
                    ) 
                print(response)
            # Put each of these snapshots in an S3 bucket

                if 'SnapshotId' in response.keys() and response['SnapshotId']!='':
                     logger.info(
                          {
                            "step": "ebs_snapshots",
                            "function": "main",
                            "instance_id": instance_id,
                            "incident_id": incident_id,
                            "message": f"Successfully created EBS snapshot"
                            })
                else:
                     logger.error(
                          {
                            "step": "ebs_snapshots",
                            "function": "main",
                            "instance_id": instance_id,
                            "incident_id": incident_id,
                            "message": f"Error in creating EBS snapshot"
                            })
                    

            except Exception as e:
                logger.exception({
                    "incident_id": incident_id,
                    "step": "ebs_snapshots",
                    "instance_id": instance_id,
                    "message":"Exception occurred when creating snapshot for volume:",
                    "error": str(e)
                })



vols = ['vol-0ea89318869f3b3e7','vol-0dc1237660cd35cd4']
instance_id=''
incident_id=''
main(vols,instance_id,incident_id)
