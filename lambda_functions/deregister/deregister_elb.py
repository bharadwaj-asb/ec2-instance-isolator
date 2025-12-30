import boto3


# Function to remove from ELB v2
def elb2(instance_id, target_group_arn):
    try:
        client = boto3.client('elbv2')
    except Exception as e:
        print(f'Exception occurred when creating auto-scaling client: {e}')


    try:
        response = client.deregister_targets(
            TargetGroupArn = target_group_arn,
            Targets=[
                {
                    'Id': instance_id
                }
                ]
            )
        print(f'Successfully deregistered instance: {instance_id} from ELB v2')
    except Exception as e:
        print(f'Exception occurred when deregistering instance from elbv2: {e}')

if __name__ == '__main__':
    instance_id = 'i-0b2f164b1f525e017'
    elb_name = 'test-elb-1'
    target_group_arn = 'arn:aws:elasticloadbalancing:ap-south-1:961341555743:targetgroup/test-tg/cf8a311eeede17b1'
    elb2(instance_id, target_group_arn)