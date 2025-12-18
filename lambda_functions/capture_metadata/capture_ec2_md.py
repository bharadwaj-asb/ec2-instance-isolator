import boto3

client = boto3.client('ec2')

def main(instance_id):
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
                raise Exception('Instance is already quarantined')
    except KeyError as k:
        print(f'Exception occurred {k} Key not found')
    except Exception as e:
        print(f'Exception occurred {e}')
        return
    

    # Getting instance data
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        if 'Instances' not in response.keys():
            print(f'No instance found with Instance ID: {instance_id}')
            return 
        print(response)

    except Exception as e:
        print(f'Exception occurred {e}')


if __name__ == "__main__":
    instance_id = 'i-0299e660d99907b1d'
    main(instance_id)