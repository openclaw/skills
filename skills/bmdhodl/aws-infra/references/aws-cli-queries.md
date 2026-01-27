# AWS CLI Query Patterns

## Identity / Account
- `aws sts get-caller-identity`
- `aws iam list-account-aliases`

## EC2
- Instances: `aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name,InstanceType,Tags]'`
- Security groups: `aws ec2 describe-security-groups`
- Public IPs: `aws ec2 describe-instances --query 'Reservations[].Instances[?PublicIpAddress!=null].[InstanceId,PublicIpAddress]'`

## S3
- Buckets: `aws s3api list-buckets`
- Bucket ACL: `aws s3api get-bucket-acl --bucket <bucket>`
- Public access: `aws s3api get-public-access-block --bucket <bucket>`

## IAM
- Users: `aws iam list-users`
- Roles: `aws iam list-roles`
- Access keys (metadata): `aws iam list-access-keys --user-name <user>`

## Lambda
- Functions: `aws lambda list-functions`
- Errors (CloudWatch): use logs insights

## ECS / EKS
- ECS clusters: `aws ecs list-clusters`
- ECS services: `aws ecs list-services --cluster <cluster>`
- EKS clusters: `aws eks list-clusters`

## RDS
- Instances: `aws rds describe-db-instances`

## CloudWatch Logs (Insights)
- Start query:
  `aws logs start-query --log-group-name <group> --start-time <epoch> --end-time <epoch> --query-string '<query>'`
- Get results:
  `aws logs get-query-results --query-id <id>`

## Billing / Cost Explorer
- `aws ce get-cost-and-usage --time-period Start=YYYY-MM-DD,End=YYYY-MM-DD --granularity MONTHLY --metrics 'UnblendedCost'`

## Common write actions (confirm before running)
- Scale ECS service: `aws ecs update-service --cluster <cluster> --service <svc> --desired-count N`
- Update ASG: `aws autoscaling update-auto-scaling-group --auto-scaling-group-name <name> --desired-capacity N`
- S3 delete: `aws s3 rm s3://bucket/key`
