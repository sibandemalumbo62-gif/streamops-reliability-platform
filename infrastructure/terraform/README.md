# Terraform AWS Infrastructure

This directory contains Terraform configurations for deploying StreamOps Reliability Platform to AWS.

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- AWS account with sufficient permissions

## Setup

1. **Copy the example variables file:**
```bash
cp terraform.tfvars.example terraform.tfvars
```

2. **Edit terraform.tfvars with your configuration:**
```bash
# Update region, environment, passwords, etc.
```

3. **Initialize Terraform:**
```bash
terraform init
```

## Deployment

### 1. Create S3 backend for state (one-time setup)
```bash
aws s3api create-bucket --bucket streamops-terraform-state --region us-east-1
aws s3api put-bucket-versioning --bucket streamops-terraform-state --versioning-configuration Status=Enabled
aws dynamodb create-table --table-name streamops-terraform-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --region us-east-1
```

### 2. Plan the deployment:
```bash
terraform plan -out=tfplan
```

### 3. Apply the deployment:
```bash
terraform apply tfplan
```

## Outputs

After deployment, Terraform will output important values:

- `cluster_endpoint`: EKS cluster endpoint
- `cluster_name`: Kubernetes cluster name
- `vpc_id`: VPC ID
- `private_subnet_ids`: Private subnet IDs
- `auth_db_endpoint`: Database endpoint
- `redis_endpoint`: Redis endpoint

## Configure kubectl

After deployment, configure kubectl to access the cluster:

```bash
aws eks update-kubeconfig --region us-east-1 --name streamops-cluster
```

## Deploy Applications

Once the infrastructure is deployed, deploy the applications:

```bash
cd ../../k8s
kubectl apply -k .
```

## Destroy

To destroy the infrastructure:

```bash
terraform destroy
```

## Modules

This configuration uses the following Terraform modules:

- **VPC**: terraform-aws-modules/vpc/aws
- **EKS**: terraform-aws-modules/eks/aws

## Security Notes

- Change default passwords in terraform.tfvars
- Enable MFA on AWS account
- Use IAM roles with least privilege
- Enable encryption for all resources
- Use private subnets for databases
- Enable VPC endpoints for private communication

## Cost Optimization

- Use Spot instances for non-critical workloads
- Enable auto-scaling for node groups
- Use reserved instances for baseline capacity
- Monitor costs with AWS Cost Explorer
