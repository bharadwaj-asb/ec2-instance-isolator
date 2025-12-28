import boto3

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


def main(instance_id):

    if is_quarantined(instance_id):
        return 

    # Getting instance data
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        if 'Instances' not in response.keys():
            print(f'No instance found with Instance ID: {instance_id}')
            return 
        print(response) # Convert to JSON file
        
        # Send security group IDs to step functions output
    except Exception as e:
        print(f'Exception occurred when fetching metadata using instance-id:{instance_id} \n {e}')

    # Get associated EC2 instance profiles
    try:
        response_for_instance_profile = client.describe_iam_instance_profile_associations(Filters=[{'Name':'instance-id','Values':[instance_id]}])
        print(response_for_instance_profile) # Convert to JSON file
    except Exception as e:
        print(f'Exception occurred when fetching IAM role using instance-id: {e}')

    # Get associated ASG
    # Get associated ELB target groups and elb name
    # Get associated EBS volumes


if __name__ == "__main__":
    instance_id = 'i-0299e660d99907b1d'
    main(instance_id)