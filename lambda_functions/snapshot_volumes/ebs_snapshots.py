import boto3
from datetime import datetime
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)



# Function to create snapshot and encrypt it
def main(client,vols,instance_id,incident_id): 
        snap_ids = {'SnapshotIds': []}
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
            # Put each of these snapshots in an S3 bucket

                if 'SnapshotId' in response.keys() and response['SnapshotId']!='':
                     snap_ids['SnapshotIds'].append(response['SnapshotId'])
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
        return snap_ids

# Function to upload evidence file to S3 bucket
def upload_to_s3(body,key,instance_id,incident_id):
    bucket_name = 'test-bucket-96655' # Hardcoding the dedicated bucket name for IR evidence
    try:
        client = boto3.client('s3')
    except Exception as e:
            logger.exception({
                "incident_id": incident_id,
                "step": "ebs_snapshots",
                "function": "upload_to_s3",
                "bucket_name": bucket_name,
                "error": str(e)
                })
    try:
        response = client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=body.encode("utf-8"),
            #ServerSideEncryption="aws:kms",
            #SSEKMSKeyId=kms_key, 
            #ObjectLockMode="GOVERNANCE",
            #ObjectLockRetainUntilDate=retain_until,
            ContentType="application/json"
        )
        logger.info(
             {
                  "step": "ebs_snapshots",
                  "function": "upload_to_s3",
                  "bucket_name": bucket_name,
                  "incident_id": incident_id,
                  "message": f"Uploaded {key} to S3 bucket"
        })

    except Exception as e:
                    logger.exception({
                    "incident_id": incident_id,
                    "step": "capture_ec2_md",
                    "function": "ebs_snapshots",
                    "s3_object_key": key,
                    "error": str(e)
                    })

# Function to serialize the object. Converts datetime and other types to isoformat and string respectively 
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)




def lambda_handler(event, context):
    vols = event['EBSVolumes'] # Input to be taken from step functions
    instance_id=event['InstanceId']
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

    s3_region = 'ap-south-1'
    account_id = ''
    snapshot_ids = main(vols,instance_id,incident_id)
    json_body = json.dumps(
            snapshot_ids,
            default=json_serializer,
            indent=2
        )
    s3_key = (f"{account_id}/{s3_region}/{incident_id}/snapshots/snapshotids.json")
    upload_to_s3(json_body,s3_key,instance_id,incident_id)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
