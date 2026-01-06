import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Function for checking is the provided instance is already quarantined.
def is_quarantined(client,instance_id,incident_id):
        tag_response = client.describe_tags(
        Filters=[
        {
            'Name': 'resource-id',
            'Values': [instance_id] # Getting the specific tag for the instance ID provided.
        }
        ])
        tag_values = tag_response['Tags']
        try:
            for each_tag in tag_values: # Checking if instance is already quarantined.
                if each_tag['IncidentStatus']!=None and each_tag['IncidentStatus'] == 'Quarantined' and each_tag['QuarantineTime']:
                    return True
                
        except KeyError as k:
            logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_metadata",
                "instance_id": instance_id,
                "error": str(k)
                })
        except Exception as e:
            logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_metadata",
                "instance_id": instance_id,
                "error": str(e)
                })
        return False


# Function to serialize the object. Converts datetime and other types to isoformat and string respectively 
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)



def main(client,instance_id,s3_region,account_id,incident_id):

    # If the instance is already quarantined
    if is_quarantined(instance_id): 
        return  # Move to next step or stop the entire flow using step functions
    
    basic_md = {}
    # Getting instance data
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        if 'Instances' not in response['Reservations'][0].keys():
            logger.error({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "describe_instances",
                "instance_id": instance_id,
                "message": f"Instance {instance_id} cannot be found"
                })
            return 
        basic_md['SecurityGroups'] = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Groups'] # Returns list conatining dict
        # send security group IDs to step function outputs
        basic_md['IpDetails'] = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddresses']
        basic_md['TagData'] = response['Reservations'][0]['Instances'][0]['Tags']
        logger.info(
        {
            "step": "capture_ec2_md",
            "function": "main",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully captured EC2 instance basic metadata"
            })

        return basic_md

    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "describe_instances",
                "instance_id": instance_id,
                "message":"Error occurred when describling EC2 instances using the instance-id",
                "error":str(e)
            })


# Function to fetch associated EC2 instance profiles
def get_instance_profiles(client,instance_id,incident_id):
    try:
        response_for_instance_profile = client.describe_iam_instance_profile_associations(Filters=[{'Name':'instance-id','Values':[instance_id]}])
        logger.info(
        {
            "step": "capture_ec2_md",
            "function": "get_instance_profiles",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully captured EC2 instance basic metadata"
            })

        return response_for_instance_profile['IamInstanceProfileAssociations'] 
    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "get_instance_profile",
                "instance_id": instance_id,
                "error": "Exception when fetching EC2 instance profiles: "+str(e)
            })


# Function to get associated ASG names
def get_asg_names(instance_id,incident_id):
    try:
        client = boto3.client('autoscaling')
    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "get_asg_names",
                "instance_id": instance_id,
                "error": "Exception when creating autoscaling client: "+str(e)
            })
    try:
        response = client.describe_auto_scaling_instances(InstanceIds=[instance_id])
        logger.info(
        {
            "step": "capture_ec2_md",
            "function": "get_asg_names",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully captured auto scaling information."
            })

        return [x['AutoScalingGroupName'] for x in response['AutoScalingInstances']]
    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "get_asg_names",
                "instance_id": instance_id,
                "error": "Exception when describing autoscaling instances: "+str(e)
            })


    
# Function to fetch associated EBS volumes
def get_ebs_vols(client,instance_id,incident_id):
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        logger.info(
        {
            "step": "capture_ec2_md",
            "function": "get_ebs_vols",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully captured EBS volume information."
            })
        return [x['Ebs']['VolumeId'] for x in response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']]
    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "get_ebs_vols",
                "instance_id": instance_id,
                "error": "Exception when fetching EBS volume IDs for instance: "+str(e)
            })

# Get associated ELB target groups and elb name
def get_target_groups_for_instance(instance_id,incident_id):
    target_group_arns = []
    elb_arns = []
    try:
        client = boto3.client('elbv2')
    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "get_asg_names",
                "instance_id": instance_id,
                "error": "Exception when creating ELBv2 client: "+str(e)
            })
    
    try:
        response = client.describe_target_groups(PageSize=400)
        logger.info(
        {
            "step": "capture_ec2_md",
            "function": "get_target_groups_for_instance",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully captured target groups information."
            })

    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "get_target_groups_for_instance",
                "instance_id": instance_id,
                "error": "Exception when fetching ELB target groups for instance: "+str(e)
            })

    for each_tgrp in response['TargetGroups']:
        target_group_arn = each_tgrp['TargetGroupArn']
        try:
            target_health_response = client.describe_target_health(
                TargetGroupArn=target_group_arn,
                Targets=[
                    {
                        'Id': instance_id
                    }
                ]
            )
            for thd in target_health_response["TargetHealthDescriptions"]:
                if thd["Target"]["Id"] == instance_id: # Instance is registered in this target group
                    target_group_arns.append(target_group_arn)
                    elb_arns.append(each_tgrp['LoadBalancerArns'][0])
            logger.info(
            {
                "step": "capture_ec2_md",
                "function": "get_target_groups_for_instance",
                "instance_id": instance_id,
                "incident_id": incident_id,
                "message": f"Successfully captured target group health information."
                })
        except Exception as e:
            logger.exception({
                    "incident_id": incident_id,
                    "step": "capture_ec2_instance",
                    "function": "get_target_groups_for_instance",
                    "instance_id": instance_id,
                    "error": "Exception when fetching target group health for instance: "+str(e)
                })
    return {'TargetGroupArns':target_group_arns,'ELBArns':elb_arns}

# Function to fetch ELB names
def get_load_balancers_for_target_groups(elb_arns,instance_id,incident_id):
    names = []
    try:
        client = boto3.client('elbv2')
    except Exception as e:
        logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_instance",
                "function": "get_asg_names",
                "instance_id": instance_id,
                "error": "Exception when creating ELBv2 client: "+str(e)
            })

    try:
        response = client.describe_load_balancers(LoadBalancerArns=elb_arns)
        for lb in response['LoadBalancers']:
            names.append(lb['LoadBalancerName'])
        logger.info(
        {
            "step": "capture_ec2_md",
            "function": "get_load_balancers_for_target_groups",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully captured ELB names information."
            })
        return names
    except Exception as e:
            logger.exception({
                    "incident_id": incident_id,
                    "step": "capture_ec2_instance",
                    "function": "get_load_balancers_for_target_groups",
                    "instance_id": instance_id,
                    "error": "Exception when fetching ELB info for instance: "+str(e)
                })

# Function to upload evidence file to S3 bucket
def upload_to_s3(body,key,instance_id,incident_id):
    bucket_name = 'test-bucket-96655' # Hardcoding the dedicated bucket name for IR evidence
    try:
        client = boto3.client('s3')
    except Exception as e:
            logger.exception({
                "incident_id": incident_id,
                "step": "capture_ec2_md",
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
                  "step": "capture_ec2_md",
                  "function": "upload_to_s3",
                  "bucket_name": bucket_name,
                  "incident_id": incident_id,
                  "message": f"Uploaded {key} to S3 bucket"
        })

    except Exception as e:
                    logger.exception({
                    "incident_id": incident_id,
                    "step": "capture_ec2_md",
                    "function": "upload_to_s3_bucket",
                    "s3_object_key": key,
                    "error": str(e)
                    })



# Lambda handler function
def lambda_handler(event, context):
    try:
        client = boto3.client('ec2')
    except Exception as e:
        logger.exception({
            "incident_id": incident_id,
            "step": "capture_ec2_metadata",
            "instance_id": instance_id,
            "message":"Exception occurred when creating EC2 client",
            "error": str(e)
        })
        raise
    instance_id = 'i-0299e660d99907b1d'
    s3_region = 'ap-south-1'
    account_id = ''
    incident_id = ''
    if is_quarantined(client,instance_id,incident_id):
         return
    basic_ec2_md = main(client, instance_id,s3_region,account_id,incident_id)
    instance_profile = get_instance_profiles(client, instance_id,incident_id) 
    asg_names = get_asg_names(instance_id,incident_id) # Add to step function output
    ebs_vols = get_ebs_vols(client, instance_id,incident_id) # Add to step function output
    tgrps = get_target_groups_for_instance(instance_id,incident_id) # Add to step function output
    elb_names = get_load_balancers_for_target_groups(tgrps['ELBArns'],instance_id,incident_id) # Add to step function output
    final_md = {
        'BasicMetadata': basic_ec2_md,
        'InstanceProfiles': instance_profile,
        'ASGNames': asg_names,
        'EBSVolumes': ebs_vols,
        'TargetGroups': tgrps,
        'ELBNames': elb_names
    }
    json_body = json.dumps(
            final_md,
            default=json_serializer,
            indent=2
        )
    s3_key = (f"{account_id}/{s3_region}/{incident_id}/instance/metadata.json")
    upload_to_s3(json_body,s3_key,instance_id,incident_id)

    # Return value for step functions
    return_value= { 
    "instance_id": instance_id,
    "incident_id": incident_id,
    "step": "capture_ec2_md",
    "target_groups": affected_target_groups,
    "timestamp": datetime.now().isoformat() + "Z"
    }

