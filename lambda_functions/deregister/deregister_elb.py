import boto3

# Function to remove from ELB v1
def elb1(instance_id, elb_name): 
    try:
        client = boto3.client('elb')
    except Exception as e:
        print(f'Exception occurred when creating auto-scaling client: {e}')

    try:
        response = client.deregister_instances_from_load_balancer(
        LoadBalancerName = elb_name,
        Instances=[
            {
                'InstanceId': instance_id 
            }
        ])
        if 'Instances' in response.keys() and response['Instances']!= []:
            print(f'Successfully deregistered instance: {instance_id}')
            return
        else:
            print(f'Deregistration failed for instance: {instance_id} from ELB v1')
    except Exception as e:
        print(f'Exception occurred when deregistering instance: {e}')

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
        print(f'Successfully deregistered instance: {instance_id}')
    except Exception as e:
        print(f'Exception occurred when deregistering instance: {e}')

if __name__ == '__main__':
    instance_id = ''
    elb_name = ''
    target_group_arn = ''
    elb1(instance_id, elb_name)
    elb2(instance_id, target_group_arn)