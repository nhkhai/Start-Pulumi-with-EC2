import pulumi
import pulumi_aws as aws

# --- Configuration ---
stack = pulumi.get_stack() # pulumi.dev
project_name = pulumi.get_project() # from Pulumi.yaml: name: Start-Pulumi-with-EC2

config = pulumi.Config('workshop-config')
org = config.require('org')
github_org = config.require('githubOrg')
pulumi_org = config.require('pulumiOrg')

aws_config = pulumi.Config('aws')
aws_environment = aws_config.require_object('defaultTags')['tags']['Environment']
aws_managed_by = aws_config.require_object('defaultTags')['tags']['ManagedBy']
aws_git_repo = aws_config.require_object('defaultTags')['tags']['GitRepo']

# --- 1. Create VPC and Networking ---
vpc = aws.ec2.Vpc("app-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    tags={"Name": f"{org}-{stack}-{project_name}-vpc"})

internet_gateway = aws.ec2.InternetGateway("app-igw",
    vpc_id=vpc.id,
    tags={"Name": f"{org}-{stack}-{project_name}-igw"})

route_table = aws.ec2.RouteTable("app-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.id,
        ),
    ],
    tags={"Name": f"{org}-{stack}-{project_name}-rt"})

subnet = aws.ec2.Subnet("app-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": f"{org}-{stack}-{project_name}-subnet"})

route_table_association = aws.ec2.RouteTableAssociation("app-rta",
    subnet_id=subnet.id,
    route_table_id=route_table.id)

# --- 2. Create Security Group ---
security_group = aws.ec2.SecurityGroup("web-sg",
    description="Allow HTTP access to EC2 instance",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=80, to_port=80, protocol="tcp", cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0, to_port=0, protocol="-1", cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={"Name": f"{org}-{stack}-{project_name}-security-group"})

# --- 3. Get Latest Amazon Linux AMI ---
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        aws.ec2.GetAmiFilterArgs(name="name", values=["amzn2-ami-hvm-*-x86_64-gp2"]),
        aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
    ])

# --- 4. User Data Script ---
user_data_script = f"""#!/bin/bash
yum update -y
yum install -y httpd aws-cli git

# Start Apache
systemctl start httpd
systemctl enable httpd

# Get instance metadata  
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_TYPE=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/instance-type)
AVAILABILITY_ZONE=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION=$(echo $AVAILABILITY_ZONE | sed 's/.$//')

# Set Pulumi configuration values
PROJECT_NAME="{project_name}"
STACK="{stack}"
ORG="{org}"
ENVIRONMENT="{aws_environment}"
MANAGED_BY="{aws_managed_by}"
GIT_REPO="{aws_git_repo}"


# Create simple HTML page directly
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>EC2 Instance & Pulumi Info</title>
    <style>
        body {{ font-family: Arial; background: #222; color: #eee; padding: 40px; }}
        .container {{ border: 1px solid #00ff99; padding: 40px; background: #333; border-radius: 12px; margin-bottom: 20px; }}
        .pulumi-container {{ border: 1px solid #ff6b35; padding: 40px; background: #333; border-radius: 12px; }}
        h1 {{ color: #00ff99; }}
        h2 {{ color: #ff6b35; }}
        h3 {{ color: #ccc; margin-top: 25px; margin-bottom: 10px; border-bottom: 1px solid #555; padding-bottom: 5px; }}
        .highlight {{ color: #00ff99; font-weight: bold; }}
        small {{ color: #999; font-style: italic; }}
    </style>
</head>
<body>
    <!-- EC2 Instance Information -->
    <div class="container">
        <h1>🖥️ EC2 Instance Information</h1>
        <p><b>Instance ID:</b> INSTANCE_ID_PLACEHOLDER</p>
        <p><b>Instance Type:</b> INSTANCE_TYPE_PLACEHOLDER</p>
        <p><b>Availability Zone:</b> AVAILABILITY_ZONE_PLACEHOLDER</p>
        <p><b>Region:</b> REGION_PLACEHOLDER</p>
    </div>
    
    <!-- Pulumi Deployment Information -->
    <div class="pulumi-container">
        <h2>⚡ Pulumi Deployment Information</h2>
        
        <h3>1. Project Details</h3>
        <p><b>Project Name:</b> <span class="highlight">PROJECT_NAME_PLACEHOLDER</span></p>
        <p><b>Stack:</b> <span class="highlight">STACK_PLACEHOLDER</span></p>
        
        <h3>2. Resource Naming & Tags</h3>
        <p><b>AWS Resource Prefix:</b> <span class="highlight">ORG_PLACEHOLDER</span></p>
        <p><b>Tags Applied:</b></p>
        <ul>
            <li><b>Environment:</b> <span class="highlight">ENVIRONMENT_PLACEHOLDER</span></li>
            <li><b>ManagedBy:</b> <span class="highlight">MANAGED_BY_PLACEHOLDER</span></li>
            <li><b>GitRepo:</b> <span class="highlight">GIT_REPO_PLACEHOLDER</span></li>
        </ul>
        <small>Example: This VPC is named "ORG_PLACEHOLDER-STACK_PLACEHOLDER-PROJECT_NAME_PLACEHOLDER-vpc" and tagged with Environment=ENVIRONMENT_PLACEHOLDER</small>
        
    </div>
</body>
</html>
EOF


# Replace placeholders with actual values
sed -i "s/INSTANCE_ID_PLACEHOLDER/$INSTANCE_ID/g" /var/www/html/index.html
sed -i "s/INSTANCE_TYPE_PLACEHOLDER/$INSTANCE_TYPE/g" /var/www/html/index.html  
sed -i "s/AVAILABILITY_ZONE_PLACEHOLDER/$AVAILABILITY_ZONE/g" /var/www/html/index.html
sed -i "s/REGION_PLACEHOLDER/$REGION/g" /var/www/html/index.html

sed -i "s/PROJECT_NAME_PLACEHOLDER/$PROJECT_NAME/g" /var/www/html/index.html
sed -i "s/STACK_PLACEHOLDER/$STACK/g" /var/www/html/index.html
sed -i "s/ORG_PLACEHOLDER/$ORG/g" /var/www/html/index.html
sed -i "s/ENVIRONMENT_PLACEHOLDER/$ENVIRONMENT/g" /var/www/html/index.html
sed -i "s/GIT_REPO_PLACEHOLDER/$GIT_REPO/g" /var/www/html/index.html
sed -i "s/MANAGED_BY_PLACEHOLDER/$MANAGED_BY/g" /var/www/html/index.html
"""

# --- 5. Create EC2 Instance ---
ec2_instance = aws.ec2.Instance("web-server-instance",
    instance_type="t2.micro",
    ami=ami.id,
    subnet_id=subnet.id,
    vpc_security_group_ids=[security_group.id],
    user_data=user_data_script,
    tags={
        "Name": f"{org}-{stack}-{project_name}-instance",
    })

# --- Outputs ---
pulumi.export("github_org", github_org)
pulumi.export("pulumi_org", pulumi_org)
pulumi.export("instance_id", ec2_instance.id)
pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("public_dns", ec2_instance.public_dns)
pulumi.export("web_url", ec2_instance.public_ip.apply(lambda ip: f"http://{ip}"))