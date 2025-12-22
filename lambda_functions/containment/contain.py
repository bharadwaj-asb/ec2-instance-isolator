import boto3

try:
    client = boto3.client('ec2')
except Exception as e:
    print(f'Exception occurred when creating EC2 or security group client(s): {e}')

def main(instance_id,sg_id):
    try:
        # Block for creating security group
        r1 = client.create_security_group(
            Description='Security Group for isolating an EC2 instance',
            GroupName='SecurityGroupForIsolation',
            # VpcId can be specified if needed.
            TagSpecifications=[
                {
                'ResourceType': 'security-group',
                'Tags': [
                    {
                        'Key': 'Purpose',
                        'Value': 'Isolation'
                    }]}])
        
        group_id = r1['GroupId']
        # An entire block just to remove any ingress and egress rules that are created by default for new SGs.
        r1 = client.describe_security_group_rules(
            Filters=[
                {
                    'Name':'group-id',
                    'Values':[group_id]
                }
            ]
        )
        for d in r1['SecurityGroupRules']:
            if d['IsEgress']:
                r2 = client.revoke_security_group_egress(
                    GroupId=group_id,
                    SecurityGroupRuleIds=[d['SecurityGroupRuleId']]
                    )
            else:
                r2 = client.revoke_security_group_ingress(
                    GroupId=group_id,
                    SecurityGroupRuleIds=[d['SecurityGroupRuleId']]
                    )
        
        # Finally modifying all security groups of the instance and replacing with the isolated group.
        response = client.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[group_id]
            )
        print(response) # To be removed
    except Exception as e:
        print(f'Exception occurred when creating security group for the instance: {instance_id} \n {e}')

if __name__ == '__main__':
    instance_id = 'i-0dcec6dd704b008d3'
    sg_id = []
    main(instance_id,sg_id)