import pulumi
import pulumi_aws as aws
import json # You need to import the json library for IAM policies

# --- Configuration ---
stack = pulumi.get_stack()
project_name = pulumi.get_project()

# Assuming you have a Pulumi.<stack>.yaml file with:
# config:
#   ll-config:org: my-organization
config = pulumi.Config('ll-config')
org = config.require('org')

# --- 1. Create Networking Resources (VPC, Subnet, IGW, etc.) ---
# This section remains unchanged as it was correctly set up.
vpc = aws.ec2.Vpc("app-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    tags={ "Name": f"{org}-{stack}-{project_name}-vpc" })

internet_gateway = aws.ec2.InternetGateway("app-igw",
    vpc_id=vpc.id,
    tags={ "Name": f"{org}-{stack}-{project_name}-igw" })

route_table = aws.ec2.RouteTable("app-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.id,
        ),
    ],
    tags={ "Name": f"{org}-{stack}-{project_name}-rt" })

subnet = aws.ec2.Subnet("app-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={ "Name": f"{org}-{stack}-{project_name}-subnet" })

route_table_association = aws.ec2.RouteTableAssociation("app-rta",
    subnet_id=subnet.id,
    route_table_id=route_table.id)

# --- 2. Create a Security Group ---
# This section remains unchanged.
security_group = aws.ec2.SecurityGroup("web-sg",
    description="Enable HTTP and SSH access to EC2 instance",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22, to_port=22, protocol="tcp", cidr_blocks=["0.0.0.0/0"], description="Allow SSH access",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            from_port=80, to_port=80, protocol="tcp", cidr_blocks=["0.0.0.0/0"], description="Allow HTTP access",
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0, to_port=0, protocol="-1", cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={ "Name": f"{org}-{stack}-{project_name}-security-group" })

# --- 3. Select an Amazon Machine Image (AMI) ---
# This section remains unchanged.
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        aws.ec2.GetAmiFilterArgs(name="name", values=["amzn2-ami-hvm-*-x86_64-gp2"]),
        aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
    ])

# --- 4. NEW: Create S3 Bucket for Application Code ---
# This private S3 bucket will store the app.zip artifact uploaded by GitHub Actions.
app_bucket = aws.s3.Bucket("app-bucket")

# --- 5. NEW: Create IAM Role for the EC2 Instance ---
# This role grants the EC2 instance the permissions it needs to access other AWS services.
ec2_role = aws.iam.Role("ec2-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": { "Service": "ec2.amazonaws.com" },
        }]
    }))

# Create an IAM policy that grants permissions to read from the S3 bucket
# and to describe EC2 tags (to get the instance's own 'Name' tag).
s3_ec2_policy = aws.iam.Policy("s3-ec2-policy",
    policy=app_bucket.arn.apply(lambda arn: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": ["s3:GetObject"],
                "Effect": "Allow",
                "Resource": f"{arn}/*" # Grant read access to all objects in the bucket
            },
            {
                "Action": ["ec2:DescribeTags"], # Grant permission to read tags
                "Effect": "Allow",
                "Resource": "*" # Required for describe-tags action
            }
        ]
    })))

# Attach the policy to the role.
aws.iam.RolePolicyAttachment("ec2-policy-attachment",
    role=ec2_role.name,
    policy_arn=s3_ec2_policy.arn)

# Create an instance profile, which is a container for an IAM role that you can
# use to pass role information to an EC2 instance when the instance starts.
instance_profile = aws.iam.InstanceProfile("ec2-instance-profile", role=ec2_role.name)

# --- 6. NEW: Define the User Data Bootstrapper Script ---
# This script runs on the EC2 instance at first boot. Its only job is to download,
# unzip, and execute the main application setup script from the S3 bucket.
user_data_bootstrapper = app_bucket.id.apply(
    lambda bucket_name: f"""#!/bin/bash
yum update -y
yum install -y aws-cli unzip

# Download the application from S3
aws s3 cp s3://{bucket_name}/app.zip /tmp/app.zip

# Unzip and run the setup script from the 'app' directory
unzip /tmp/app.zip -d /
chmod +x /app/setup.sh
/app/setup.sh
"""
)

# --- 7. Create the EC2 Instance (Now with IAM Role and User Data) ---
ec2_instance = aws.ec2.Instance("web-server-instance",
    instance_type="t2.micro",
    ami=ami.id,
    subnet_id=subnet.id,
    vpc_security_group_ids=[security_group.id],
    
    # MODIFIED: Attach the IAM role and the user data script
    iam_instance_profile=instance_profile.name,
    user_data=user_data_bootstrapper,
    
    tags={
        "Name": f"{org}-{stack}-{project_name}-instance",
    })

# --- Outputs ---
# Your original outputs, plus the new S3 bucket name which is essential for the CI/CD workflow.
pulumi.export("project_name", project_name)
pulumi.export("stack", stack)
pulumi.export("instance_id", ec2_instance.id)
pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("public_dns", ec2_instance.public_dns)
pulumi.export("security_group_id", security_group.id)
pulumi.export("s3_bucket_name", app_bucket.id) # <-- CRITICAL for GitHub Actions