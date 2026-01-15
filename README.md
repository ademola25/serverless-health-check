# Serverless Health Check API with CI/CD

A serverless health check API deployed to AWS using Terraform and GitHub Actions.

## Development Notes

This project demonstrates both individual rapid development (direct commits to main) and team collaboration workflows (pull requests for later features). 

The initial infrastructure was built with direct commits to enable fast iteration and immediate CI/CD testing. Pull requests are used for subsequent enhancements to demonstrate collaborative development practices.

In production team environments, I use feature branches with pull requests and code reviews before merging to main.


## Prerequisites

### Required Tools
- AWS Account with administrative access
- GitHub account
- AWS CLI (optional, for retrieving endpoints)

### GitHub Secrets Configuration

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `AWS_ACCESS_KEY_ID` - Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret access key

### One-Time Backend Setup

Before first deployment:
1. Create an S3 bucket in AWS for Terraform state storage
2. Create a DynamoDB table named `terraform-state-lock` (optional, for state locking)
3. Update `terraform/backend.tf` with your bucket name:
```hcl
terraform {
  backend "s3" {
    bucket         = "your-bucket-name"  # ← Replace with your S3 bucket name
    key            = "serverless-health-check/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## How the CI/CD Pipeline Works

The GitHub Actions pipeline automates infrastructure deployment with environment separation:

### Pipeline Triggers

1. **Push to main branch** → Automatically deploys to staging
2. **Manual workflow dispatch** → Deploy to staging or production (with approval)

### Pipeline Steps

1. **Checkout code** - Pulls latest code from repository
2. **Setup Python 3.11** - Configures Python environment
3. **Package Lambda** - Installs dependencies and creates deployment zip
4. **Configure AWS credentials** - Authenticates using GitHub secrets
5. **Initialize Terraform** - Sets up backend and downloads providers
6. **Validate configuration** - Checks formatting and syntax
7. **Plan infrastructure** - Shows what will be created/changed
8. **Apply changes** - Creates/updates AWS resources
9. **Test endpoint** - Verifies the deployed API works
10. **Upload artifact** - Stores Lambda package for reference

### Environment Protection

- **Staging**: Deploys automatically on push to main
- **Production**: Requires manual trigger + approval gate

## Deploying to Staging

### Automatic Deployment (Push to Main)
```bash
git add .
git commit -m "Your changes"
git push origin main
```

The pipeline automatically deploys to staging. Monitor progress in the GitHub Actions tab.

### Manual Deployment

1. Go to **Actions** tab in GitHub
2. Click **Deploy Serverless Health Check**
3. Click **Run workflow** (top right)
4. Select environment: **staging**
5. Click **Run workflow**

## Deploying to Production

1. Go to **Actions** → **Deploy Serverless Health Check**
2. Click **Run workflow**
3. Select environment: **prod**
4. Click **Run workflow**
5. When the approval gate appears, click **Review deployments**
6. Check **prod-approval** and click **Approve and deploy**

**Setup approval gate:**
- Go to Settings → Environments → Create "prod-approval"
- Add required reviewers
- Save protection rules

## Testing the Deployed Endpoint

### Note on Live Demo Endpoints

For reviewer convenience, the example API endpoints below are **live deployments** in my AWS account. These allow immediate testing without deployment setup. The resources are isolated to this project, contain no sensitive data, and will be cleaned up after the interview process.

### Quick Test (Using Demo Endpoints)

You can test the API immediately using these live endpoints:

**Staging endpoint:**
```bash
curl https://e07ts9hne5.execute-api.us-east-1.amazonaws.com/health
```

**Production endpoint:**
```bash
curl https://sci40clcj3.execute-api.us-east-1.amazonaws.com/health
```

**POST request example:**
```bash
curl -X POST https://e07ts9hne5.execute-api.us-east-1.amazonaws.com/health \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Expected response:**
```json
{
  "status": "healthy",
  "message": "Request processed and saved.",
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Get Your Own Endpoints (After Deployment)

After deploying to your AWS account, retrieve your endpoints:
```bash
cd terraform
terraform init -backend-config="key=serverless-health-check/staging/terraform.tfstate"
terraform output api_endpoint
```

Or using AWS CLI:
```bash
# Get staging endpoint
aws apigatewayv2 get-apis --query 'Items[?Name==`staging-health-check-api`].ApiEndpoint' --output text

# Get production endpoint
aws apigatewayv2 get-apis --query 'Items[?Name==`prod-health-check-api`].ApiEndpoint' --output text
```

## Design Decisions

### Infrastructure

**Terraform Modules**: Created a reusable module (`terraform/modules/serverless-health-check`) to promote code reuse and maintainability across environments.

**Environment Separation**: Used `.tfvars` files (`staging.tfvars`, `prod.tfvars`) for environment-specific configuration, enabling easy multi-environment management with a single codebase.

**Resource Naming**: Followed `{env}-{resource}-{name}` convention (e.g., `staging-health-check-function`) for clear resource identification.

**IAM Least Privilege**: Lambda function has only essential permissions:
- CloudWatch: Create logs and write log events
- DynamoDB: PutItem only on the specific environment table
- No unnecessary read, delete, or administrative permissions

**API Gateway Choice**: Used HTTP API instead of REST API for lower latency, reduced cost, and simpler configuration.

**DynamoDB Billing**: Chose on-demand pricing for unpredictable traffic patterns and automatic scaling.

### CI/CD

**Automated Staging**: Deploys automatically on main branch push for fast development feedback.

**Manual Production**: Requires manual trigger and approval for production safety and change control.

**Lambda Packaging**: Automated dependency installation ensures consistent deployments without committing packages to source control.

**Health Checks**: Automated endpoint testing after deployment verifies infrastructure is working correctly.

### Security

**Secrets Management**: AWS credentials stored as GitHub encrypted secrets, never in source code.

**State Security**: Terraform state stored in encrypted S3 bucket with versioning enabled for audit trail and recovery.

**Network Security**: Lambda not publicly accessible, only invocable through API Gateway with proper IAM permissions.

## Assumptions

- AWS region is `us-east-1` (configurable via `.tfvars`)
- Python 3.11 runtime for Lambda
- GitHub Actions has network access to AWS services
- Single AWS account used for both staging and production (separated by naming)
- No existing resources with conflicting names

## AWS Resources Created

### Per Environment (Staging and Production)

- Lambda Function: `{env}-health-check-function`
- API Gateway: `{env}-health-check-api`
- DynamoDB Table: `{env}-requests-db`
- IAM Role: `{env}-health-check-lambda-role`
- CloudWatch Log Group: `/aws/lambda/{env}-health-check-function`

### Shared (Manual Setup)

- S3 Bucket: Terraform state storage
- DynamoDB Table: State locking (optional)

## Cleanup
```bash
cd terraform

# Destroy staging
terraform init -backend-config="key=serverless-health-check/staging/terraform.tfstate"
terraform destroy -var-file="environments/staging.tfvars"

# Destroy production
terraform init -backend-config="key=serverless-health-check/prod/terraform.tfstate"
terraform destroy -var-file="environments/prod.tfvars"
```