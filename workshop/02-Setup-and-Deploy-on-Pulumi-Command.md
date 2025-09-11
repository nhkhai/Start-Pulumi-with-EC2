# Setup and Deploy on Pulumi Command 

## What You Need

- AWS Account
- AWS AccessKey and SecretAccessKey
- GitHub account
- Python

## Step 1: Get the Code

1. Fork this repository to your GitHub account
2. In your forked repository page, click on **Code**, then click on the **+** button under **Codespaces**, to Create a codespace on dev
3. Wait for the codespace to finish setting up (this may take 3-4 minutes)
4. Once it's ready, open the terminal in your codespace and run `aws configure` to configure the aws credentials 
    - Enter your AWS credentials when prompted:
        ```    
        AWS Access Key ID: [Your AWS Access Key]
        AWS Secret Access Key: [Your AWS Secret Key]
        Default region name: ap-southeast-1
        Default output format: json
        ```


## Step 2: Create AWS Role for GitHub

### Create Policy
1. Go to AWS Console → IAM → Policies → Create Policy
2. Use JSON tab, paste this:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "iam:*",
                "s3:*",
                "sts:AssumeRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

3. Name it: `PulumiWorkshopPolicy`

### Create Role
1. IAM → Roles → Create Role
2. Select "Web identity" 
3. Choose "GitHub" as identity provider (if GitHub isn't available as an option, select "Custom trust policy" last step)
4. Set trust policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/Start-Pulumi-with-EC2:*"
                }
            }
        }
    ]
}
```

**Replace:**
- `YOUR_ACCOUNT_ID` with your AWS account ID
- `YOUR_GITHUB_USERNAME` with your GitHub username

5. Attach the `PulumiWorkshopPolicy`
6. Name the role: `GitHubActionsPulumiRole`
7. **Copy the Role ARN** - you need this next

### Setup OIDC

1. IAM → Identity providers → Add provider
2. Provider type: OpenID Connect
3. Provider URL: `https://token.actions.githubusercontent.com`
4. Audience: `sts.amazonaws.com`

## Step 3: Get Pulumi Token

1. Go to [app.pulumi.com](https://app.pulumi.com) 
2. Sign up/login
3. Settings → Access Tokens → New Access Token
4. **Copy the token**

## Step 4: Add GitHub Secrets

Go to your repo → Settings → Secrets → Actions:

Add these secrets:
- `AWS_ROLE_ARN`: Your role ARN from step 2
- `PULUMI_ACCESS_TOKEN`: Your Pulumi token from step 3

## Step 5: Deploy!

```bash
cd infra
pulumi preview # dry run and preview all the things which will be created 
pulumi up --stack dev
```

## Step 6: See Your Website

After deployment completes:
1. Run `pulumi stack output web_url --stack dev` to get your URL
2. Open the URL in browser → See your EC2 info page!

## Step 7: Clean Up (IMPORTANT!)

**Don't forget this or you'll get charged!**

```bash
cd infra
pulumi destroy 
```
(Note: Don't run `pulumi stack rm dev` to remove stack, as we gonna use it in the next step)

## Troubleshooting

**"Access Denied"** → Check your IAM role permissions and trust policy
**"OIDC Provider not found"** → Follow step "Setup OIDC" above  
**"Pulumi token invalid"** → Get a new token from app.pulumi.com

## What You Just Built

🎉 You created:
- Complete AWS network (VPC, subnets, routing)
- EC2 instance with web server
- Security groups

All with code that you can deploy and destroy safely!

Next: Let's modify some settings! 🚀