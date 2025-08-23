# Simple EC2 Web App with Pulumi

This project deploys a simple web application to an AWS EC2 instance using Pulumi.

## What it does

- Creates an EC2 instance with a web server
- Displays instance information on a web page
- All resources can be destroyed with `pulumi destroy`

## Project Structure

```
├── .github/workflows/
│   ├── deploy-ec2.yml               # Main deploy/destroy workflow
│   └── destroy-ec2.yml              # Dedicated destroy workflow  
├── infra/
│   ├── __main__.py                  # Pulumi infrastructure code
│   ├── Pulumi.yaml                  # Project config
│   ├── Pulumi.dev.yaml              # Dev environment config
│   └── requirements.txt             # Python dependencies
└── README.md
```

## Required GitHub Secrets

Set these in your GitHub repository settings:

- `AWS_ROLE_ARN`: Your AWS IAM role for GitHub Actions
- `PULUMI_ACCESS_TOKEN`: Your Pulumi access token

## Deploy

1. Push to the `dev` branch
2. GitHub Actions will automatically deploy
3. Access your web app at the provided URL

## Destroy

You have multiple options to destroy all resources:

### Option 1: GitHub Actions (Recommended)
1. Go to **Actions** tab in your GitHub repository
2. Click **"Deploy EC2 App"** workflow
3. Click **"Run workflow"**
4. Select **"destroy"** from the action dropdown
5. Click **"Run workflow"** → All resources will be destroyed

### Option 2: Dedicated Destroy Workflow
1. Go to **Actions** tab in your GitHub repository  
2. Click **"Destroy EC2 Infrastructure"** workflow
3. Click **"Run workflow"**
4. Type **"DESTROY"** in the confirmation field
5. Select the stack (dev)
6. Click **"Run workflow"** → All resources will be destroyed

### Option 3: Local Command
```bash
cd infra
pulumi destroy --stack dev
```

## Local Development

```bash
cd infra
pip install -r requirements.txt
pulumi up --stack dev
```

That's it! Keep it simple. 🚀
