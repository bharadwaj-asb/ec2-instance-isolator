import boto3
from datetime import datetime

try:
    client = boto3.client('ec2')
except Exception as e:
    print(f'Exception occurred when creating EC2 client: {e}')


# Function to create snapshot and encrypt it
def main(vols): 
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
            except Exception as e:
                print(f'Exception occurred when creating snapshot for volume: {each_vol} : {e}')


if __name__ == '__main__':
    vols = ['vol-0ea89318869f3b3e7','vol-0dc1237660cd35cd4']
    main(vols)
