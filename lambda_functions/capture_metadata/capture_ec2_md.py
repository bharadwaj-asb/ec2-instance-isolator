import boto3
import json
from datetime import datetime

try:
    client = boto3.client('ec2')
except Exception as e:
    print(f'Exception occurred when creating EC2 client: {e}')

# Function for checking is the provided instance is already quarantined.
def is_quarantined(instance_id):
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
            print(f'Exception occurred {k} Key not found')
        except Exception as e:
            print(f'Exception occurred {e}')
        return False


# Function to serialize the object. Converts datetime and other types to isoformat and string respectively 
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

# Function to upload evidence file to S3 bucket
def upload_to_s3(body,key):
    bucket_name = '' # Hardcoding the dedicated bucket name for IR evidence
    try:
        client = boto3.client('s3')
    except Exception as e:
        print(f'Error occurred when creating s3 client: {e}')
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
    except Exception as e:
        print(f'Error occurred when putting object {key} to S3 bucket {bucket_name}: {e}')



def main(instance_id,s3_region,account_id,incident_id):

    if is_quarantined(instance_id):
        return 

    # Getting instance data
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        if 'Instances' not in response.keys():
            print(f'No instance found with Instance ID: {instance_id}')
            return 
        print(response) # Convert to JSON file
        json_body = json.dumps(
            response,
            default=json_serializer,
            indent=2
        )
        s3_key = (f"{account_id}/{s3_region}/{incident_id}/execution/detach_asg.json")
        upload_to_s3(json_body,s3_key)
        # Send security group IDs to step functions output
    except Exception as e:
        print(f'Exception occurred when fetching metadata using instance-id:{instance_id} \n {e}')

# Function to fetch associated EC2 instance profiles
def get_instance_profiles(instance_id):
    try:
        response_for_instance_profile = client.describe_iam_instance_profile_associations(Filters=[{'Name':'instance-id','Values':[instance_id]}])
        return response_for_instance_profile['IamInstanceProfileAssociations'] 
    except Exception as e:
        print(f'Exception occurred when fetching IAM role using instance-id: {e}')

# Function to get associated ASG names
def get_asg_names(instance_id):
    try:
        client = boto3.client('autoscaling')
    except Exception as e:
        print(f'Exception occurred when creating autoscaling client: {e}')
    try:
        response = client.describe_auto_scaling_instances(InstanceIds=[instance_id])
        return [x['AutoScalingGroupName'] for x in response['AutoScalingInstances']]
    except Exception as e:
        print(f'Exception occurred when fetching autoscaling group names: {e}')

    
# Function to fetch associated EBS volumes
def get_ebs_vols(instance_id):
    try:
        client = boto3.client('ec2')
    except Exception as e:
        print(f'Exception occurred when creating EC2 client: {e}')
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        return [x['Ebs']['VolumeId'] for x in response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']]
    except Exception as e:
        print(f'Exception occurred when fetching volume IDs for the EC2 instance: {e}')

# Get associated ELB target groups and elb name
def get_target_groups_for_instance(instance_id):
    target_group_arns = []
    elb_arns = []
    try:
        client = boto3.client('elbv2')
    except Exception as e:
        print(f'Exception occurred when creating ELBv2 client: {e}')
    
    try:
        response = client.describe_target_groups(PageSize=400)
    except Exception as e:
        print(f'Exception occurred when describing ELB target groups: {e}')

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
        except Exception as e:
            print(f'Exception occurred when describing ELB target group health: {e}')
    return {'TargetGroupArns':target_group_arns,'ELBArns':elb_arns}

# Function to fetch ELB names
def get_load_balancers_for_target_groups(elb_arns):
    names = []
    try:
        client = boto3.client('elbv2')
    except Exception as e:
        print(f'Exception occurred when creating ELBv2 client: {e}')

    try:
        response = client.describe_load_balancers(LoadBalancerArns=elb_arns)
        for lb in response['LoadBalancers']:
            names.append(lb['LoadBalancerName'])
        return names
    except Exception as e:
        print(f'Exception occurred when describing Load Balancers: {e}')


# Lambda handler function
if __name__ == "__main__":
    instance_id = 'i-0299e660d99907b1d'
    s3_region = 'ap-south-1'
    account_id = ''
    incident_id = ''
    main(instance_id,s3_region,account_id,incident_id)
    instance_profile = get_instance_profiles(instance_id) # Add to S3 bucket
    asg_names = get_asg_names(instance_id) # Add to S3 bucket and step function output
    ebs_vols = get_ebs_vols(instance_id) # Add to S3 bucket and step function output
    tgrps = get_target_groups_for_instance(instance_id) # Add to S3 bucket and step function output
    elb_names = get_load_balancers_for_target_groups(tgrps['ELBArns']) # Add to S3 bucket and step function output

