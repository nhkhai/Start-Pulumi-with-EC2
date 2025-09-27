import pulumi
import pulumi_aws as aws

# --- Configuration ---
stack = pulumi.get_stack()  # pulumi.dev
# from Pulumi.yaml: name: Start-Pulumi-with-EC2
project_name = pulumi.get_project()

config = pulumi.Config('workshop-config')
org = config.require('org')

aws_config = pulumi.Config('aws')
aws_environment = aws_config.require_object(
    'defaultTags')['tags']['Environment']
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
        aws.ec2.GetAmiFilterArgs(name="name", values=[
                                 "amzn2-ami-hvm-*-x86_64-gp2"]),
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
sed -i "s/stack_placeholder/$stack/g" /var/www/html/index.html

cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Pulumi EC2 Server</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            color: #333;
            padding: 40px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        h1 {{ 
            color: #2c5aa0;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .section {{
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #2c5aa0;
        }}
        
        .section h2 {{
            color: #2c5aa0;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .info-item {{
            margin-bottom: 8px;
        }}
        
        .highlight {{
            color: #2c5aa0;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Pulumi EC2 Server</h1>
        
        <div class="section">
            <h2>🖥️ Server Information</h2>
            <div class="info-item"><strong>Instance ID:</strong> <span class="highlight">INSTANCE_ID_PLACEHOLDER</span></div>
            <div class="info-item"><strong>Type:</strong> <span class="highlight">INSTANCE_TYPE_PLACEHOLDER</span></div>
            <div class="info-item"><strong>Zone:</strong> <span class="highlight">AVAILABILITY_ZONE_PLACEHOLDER</span></div>
            <div class="info-item"><strong>Region:</strong> <span class="highlight">REGION_PLACEHOLDER</span></div>
        </div>
        
        <div class="section">
            <h2>⚡ Pulumi Project</h2>
            <div class="info-item"><strong>Project:</strong> <span class="highlight">PROJECT_NAME_PLACEHOLDER</span></div>
            <div class="info-item"><strong>Stack:</strong> <span class="highlight">STACK_PLACEHOLDER</span></div>
            <div class="info-item"><strong>Organization:</strong> <span class="highlight">ORG_PLACEHOLDER</span></div>
        </div>
        
        <div class="section">
            <h2>🏷️ Resource Tags</h2>
            <div class="info-item"><strong>Environment:</strong> <span class="highlight">ENVIRONMENT_PLACEHOLDER</span></div>
            <div class="info-item"><strong>Managed By:</strong> <span class="highlight">MANAGED_BY_PLACEHOLDER</span></div>
            <div class="info-item"><strong>Git Repository:</strong> <span class="highlight">GIT_REPO_PLACEHOLDER</span></div>
        </div>
        
        <div class="footer">
            <p>✨ Created with Infrastructure as Code</p>
        </div>
    </div>
</body>
</html>
EOF



# replace placeholders with actual values
sed -i "s/instance_id_placeholder/$instance_id/g" /var/www/html/index.html
sed -i "s/instance_type_placeholder/$instance_type/g" /var/www/html/index.html  
sed -i "s/availability_zone_placeholder/$availability_zone/g" /var/www/html/index.html
sed -i "s/region_placeholder/$region/g" /var/www/html/index.html

sed -i "s/PROJECT_NAME_PLACEHOLDER/$PROJECT_NAME/g" /var/www/html/index.html
sed -i "s/ORG_PLACEHOLDER/$ORG/g" /var/www/html/index.html
sed -i "s/ENVIRONMENT_PLACEHOLDER/$ENVIRONMENT/g" /var/www/html/index.html
sed -i "s/GIT_REPO_PLACEHOLDER/$GIT_REPO/g" /var/www/html/index.html
sed -i "s/MANAGED_BY_PLACEHOLDER/$MANAGED_BY/g" /var/www/html/index.html
"""

# --- 5. Create EC2 Instance ---
ec2_instance = aws.ec2.Instance("web-server-instance",
                                instance_type="t3.small",
                                ami=ami.id,
                                subnet_id=subnet.id,
                                vpc_security_group_ids=[security_group.id],
                                user_data=user_data_script,
                                tags={
                                    "Name": f"{org}-{stack}-{project_name}-instance",
                                })

# --- Outputs ---
# pulumi.export("github_org", github_org)
# pulumi.export("pulumi_org", pulumi_org)
pulumi.export("instance_id", ec2_instance.id)
pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("public_dns", ec2_instance.public_dns)
pulumi.export("web_url", ec2_instance.public_ip.apply(
    lambda ip: f"http://{ip}"))
