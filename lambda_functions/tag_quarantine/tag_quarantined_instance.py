import boto3
from datetime import datetime

try:
    client = boto3.client('ec2')
except Exception as e:
    print(f'Exception occurred when creating EC2 client: {e}')

def main(instance_id):
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
                    }
            ])
        print(response)
    except Exception as e:
        print(f'Exception occurred when tagging the instance: {instance_id} \n {e}')

    


if __name__ == '__main__':
    instance_id = 'i-01a9e1bfa13067635'
    main(instance_id)