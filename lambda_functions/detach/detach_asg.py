import boto3

try:
    client = boto3.client('autoscaling')
except Exception as e:
    print(f'Exception occurred when creating auto-scaling client: {e}')


def main(instance_id, asg_name):
    try:
        response = client.detach_instances(
        InstanceIds=[instance_id],
        AutoScalingGroupName = asg_name,
        ShouldDecrementDesiredCapacity=False
        )
    except Exception as e:
        print(f'Exception occurred when detaching auto-scaling the the instance: {instance_id} {e}')    


if __name__ == '__main__':
    instance_id = ''
    asg_name = ''
    main(instance_id, asg_name)