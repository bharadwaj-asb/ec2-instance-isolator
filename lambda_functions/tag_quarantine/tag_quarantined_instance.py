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
                        'Value': datetime.now()
                    }
            ])
    except Exception as e:
        print(f'Exception occurred when tagging the instance: {instance_id} \n {e}')

    


if __name__ == '__main__':
    instance_id = ''
    main(instance_id)