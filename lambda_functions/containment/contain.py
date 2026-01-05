import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    client = boto3.client('ec2')
except Exception as e:
    logger.exception({
        "incident_id": incident_id,
        "step": "containment",
        "instance_id": instance_id,
        "error": str(e)
    })
    raise

def main(instance_id,sg_id,incident_id):
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
        # Block just to remove the ingress/egress rules that are created by default for new SGs.
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
        logger.info(
        {
            "step": "containment",
            "function": "main",
            "instance_id": instance_id,
            "incident_id": incident_id,
            "message": f"Successfully modified security groups and contained the instance."
            })
    except Exception as e:
        logger.exception({
        "incident_id": incident_id,
        "step": "containment",
        "instance_id": instance_id,
        "error": str(e)
    })

#if __name__ == '__main__':
instance_id = 'i-0485bd939bfd72eea'
sg_id = []
incident_id = ''
main(instance_id,sg_id,incident_id)