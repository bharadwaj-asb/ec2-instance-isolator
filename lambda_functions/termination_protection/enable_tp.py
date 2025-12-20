import boto3

try:
    client = boto3.client('ec2')
except Exception as e:
    print(f'Exception occurred when creating EC2 client: {e}')

def main(instance_id):
    try:
        response = client.modify_instance_attribute(InstanceID=instance_id, DisableApiTermination={
        'Value': True
        })
    except Exception as e:
        print(f'Exception occurred when enabling termination protection for the instance: {instance_id} \n {e}')

    


if __name__ == '__main__':
    instance_id = ''
    main(instance_id)