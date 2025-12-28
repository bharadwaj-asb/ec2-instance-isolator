import boto3

try:
    client = boto3.client('ec2')
except Exception as e:
    print(f'Exception occurred when creating EC2 client: {e}')


# Function to create snapshot and encrypt it
def main(vol_id, elb_name): 

    try:
        response = client.create_snapshot(
            VolumeId= vol_id,
            TagSpecifications=[
                {
                    'Tags': [
                        {
                            'Key': 'string',
                            'Value': 'string'
                        }
                    ]
                }
            ]
            ) 
    except Exception as e:
        print(f'Exception occurred when deregistering instance: {e}')


if __name__ == '__main__':
    instance_id = ''
    elb_name = ''
    target_group_arn = ''
    main(vol_id, elb_name)
