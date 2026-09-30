#!/usr/bin/env bash
set -euo pipefail

: "${AWS_REGION:?Set AWS_REGION to the lab region}"
export AWS_DEFAULT_REGION="$AWS_REGION"

echo "Tagged project resources"
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=cicd-book \
  --query 'ResourceTagMappingList[].ResourceARN' \
  --output table

echo "NAT gateways tagged for this project (expected: none)"
aws ec2 describe-nat-gateways \
  --filter Name=tag:Project,Values=cicd-book Name=state,Values=pending,available,deleting \
  --query 'NatGateways[].{Id:NatGatewayId,State:State,Subnet:SubnetId}' \
  --output table

echo "Project S3 buckets"
aws s3api list-buckets \
  --query 'Buckets[?starts_with(Name, `cicd-book-`)].{Name:Name,Created:CreationDate}' \
  --output table

