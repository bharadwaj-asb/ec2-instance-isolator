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
                    Description= 'This is a quarantined snapshot',
                    VolumeId= each_vol,
                    TagSpecifications=[
                        {
                            'Tags': [
                                {
                                    'Key': 'IncidentStatus',
                                    'Value': 'Quarantined'
                                },
                                {
                                    'Key': 'QuarantineTime',
                                    'Value': datetime.now()
                                }
                            ]
                        }
                    ]
                    ) 
            # Put each of these snapshots in an S3 bucket
            except Exception as e:
                print(f'Exception occurred when creating snapshot for volume: {each_vol} : {e}')


if __name__ == '__main__':
    vols = []
    main(vols)
