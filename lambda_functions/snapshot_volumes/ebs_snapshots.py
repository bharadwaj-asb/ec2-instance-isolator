import boto3
from datetime import datetime

try:
    client = boto3.client('ec2')
except Exception as e:
    print(f'Exception occurred when creating EC2 client: {e}')


# Function to create snapshot and encrypt it
def main(vols): 
    try:
        for each_vol in vols:
            response = client.create_snapshot(
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
        print(f'Exception occurred when deregistering instance: {e}')


if __name__ == '__main__':
    vols = []
    main(vols)
