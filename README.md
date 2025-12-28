## EC2 Instance Isolator

An automated, security-first incident response workflow that isolates compromised Amazon EC2 instances, prevents evidence destruction, and preserves forensic artifacts, aligned with AWS incident response best practices.

This project focuses on containment and forensic preservation, not remediation, ensuring compromised workloads are safely quarantined for investigation without interference from Auto Scaling or load-balancing mechanisms.

## Objective
Design and implement an automated incident response workflow that:
1. Preserves the compromised instance as forensic evidence
2. Prevents Auto Scaling termination and replacement
3. Isolates the instance from network traffic
4. Captures instance state and disk artifacts securely
5. Maintains auditability and investigation context
6. All actions are performed via AWS control-plane APIs, without accessing the instance itself.

## Incident Response Workflow
1. Capture EC2 control-plane metadata (pre-change state)
2. Enable termination protection on the instance
3. Detach the instance from Auto Scaling Groups
4. Isolate the instance by switching to a quarantine security group
5. Deregister the instance from load balancers
6. Create encrypted EBS snapshots of all attached volumes
7. Tag resources to mark quarantine status and investigation context

## Inspiration & References
This project is inspired by AWS incident response guidance and reference implementations, and extends them with workflow orchestration, audit visibility, and forensic-focused design choices suitable for real-world security operations.
