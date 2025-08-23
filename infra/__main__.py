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
GITHUB_ORG="{github_org}"
PULUMI_ORG="{pulumi_org}"
ENVIRONMENT="{aws_environment}"
MANAGED_BY="{aws_managed_by}"
GIT_REPO="{aws_git_repo}"


# Create simple HTML page directly
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Beautiful Pulumi EC2 Dashboard</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 20px;
            margin: 0;
            min-height: 100vh;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .main-title {{
            color: #00ff99; 
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }}
        @keyframes glow {{
            from {{ text-shadow: 3px 3px 6px rgba(0,0,0,0.5), 0 0 20px #00ff99; }}
            to {{ text-shadow: 3px 3px 6px rgba(0,0,0,0.5), 0 0 30px #00ff99, 0 0 40px #00ff99; }}
        }}
        .container {{ 
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border: 1px solid #00ff99; 
            padding: 40px; 
            background: rgba(0,0,0,0.3); 
            border-radius: 20px; 
            margin-bottom: 20px;
            animation: fadeIn 1s ease-in;
        }}
        .pulumi-container {{ 
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border: 1px solid #ff6b35; 
            padding: 40px; 
            background: rgba(0,0,0,0.3); 
            border-radius: 20px;
            animation: fadeIn 1.5s ease-in;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        h1 {{ color: #00ff99; font-size: 2.2em; text-align: center; }}
        h2 {{ color: #ff6b35; font-size: 2em; text-align: center; }}
        h3 {{ 
            color: #00ff99; 
            margin-top: 25px; 
            margin-bottom: 15px; 
            border-bottom: 2px solid rgba(0,255,153,0.3); 
            padding-bottom: 8px;
            font-size: 1.3em;
        }}
        .highlight {{ 
            color: #00ff99; 
            font-weight: bold; 
            background: rgba(0,255,153,0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .info-item {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .info-item:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,255,153,0.2);
        }}
        .tag-list {{
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }}
        .tag-list ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .tag-list li {{
            margin: 8px 0;
            padding: 5px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
            list-style-type: none;
            position: relative;
            padding-left: 30px;
        }}
        .tag-list li:before {{
            content: "🏷️";
            position: absolute;
            left: 8px;
        }}
        .example-text {{
            background: rgba(255,107,53,0.1);
            border: 1px solid rgba(255,107,53,0.3);
            padding: 10px;
            border-radius: 8px;
            font-style: italic;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        .badges {{
            text-align: center;
            margin: 30px 0;
        }}
        .badge {{
            display: inline-block;
            background: linear-gradient(45deg, #00ff99, #00cc7a);
            color: #222;
            padding: 10px 18px;
            border-radius: 25px;
            font-weight: bold;
            margin: 5px;
            box-shadow: 0 4px 12px rgba(0,255,153,0.3);
            transition: transform 0.2s ease;
        }}
        .badge:hover {{
            transform: scale(1.05);
        }}
        small {{ color: #bbb; font-style: italic; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="main-title">🚀 Beautiful Pulumi Dashboard</h1>
    </div>

    <!-- EC2 Instance Information -->
    <div class="container">
        <h1>🖥️ EC2 Instance Information</h1>
        <div class="info-grid">
            <div class="info-item">
                <p><b>Instance ID:</b> <span class="highlight">INSTANCE_ID_PLACEHOLDER</span></p>
            </div>
            <div class="info-item">
                <p><b>Instance Type:</b> <span class="highlight">INSTANCE_TYPE_PLACEHOLDER</span></p>
            </div>
            <div class="info-item">
                <p><b>Availability Zone:</b> <span class="highlight">AVAILABILITY_ZONE_PLACEHOLDER</span></p>
            </div>
            <div class="info-item">
                <p><b>Region:</b> <span class="highlight">REGION_PLACEHOLDER</span></p>
            </div>
        </div>
    </div>
    
    <!-- Pulumi Deployment Information -->
    <div class="pulumi-container">
        <h2>⚡ Pulumi Deployment Information</h2>
        
        <h3>1. Project Details</h3>
        <div class="info-grid">
            <div class="info-item">
                <p><b>Project Name:</b> <span class="highlight">PROJECT_NAME_PLACEHOLDER</span></p>
            </div>
            <div class="info-item">
                <p><b>Stack:</b> <span class="highlight">STACK_PLACEHOLDER</span></p>
            </div>
        </div>
        
        <h3>2. Resource Naming & Tags</h3>
        <p><b>AWS Resource Prefix:</b> <span class="highlight">ORG_PLACEHOLDER</span></p>
        
        <div class="tag-list">
            <p><b>Tags Applied to All Resources:</b></p>
            <ul>
                <li><b>Environment:</b> <span class="highlight">ENVIRONMENT_PLACEHOLDER</span></li>
                <li><b>ManagedBy:</b> <span class="highlight">MANAGED_BY_PLACEHOLDER</span></li>
                <li><b>GitRepo:</b> <span class="highlight">GIT_REPO_PLACEHOLDER</span></li>
            </ul>
            <div class="example-text">
                <small>💡 Example: This VPC is named "<span class="highlight">ORG_PLACEHOLDER-STACK_PLACEHOLDER-PROJECT_NAME_PLACEHOLDER-vpc</span>" and tagged with Environment=<span class="highlight">ENVIRONMENT_PLACEHOLDER</span></small>
            </div>
        </div>
        
        <h3>3. Source & Deployment Tracking</h3>
        <div class="info-grid">
            <div class="info-item">
                <p><b>GitHub Org:</b> <span class="highlight">GITHUB_ORG_PLACEHOLDER</span></p>
            </div>
            <div class="info-item">
                <p><b>Pulumi Org:</b> <span class="highlight">PULUMI_ORG_PLACEHOLDER</span></p>
            </div>
        </div>

        <div class="badges">
            <span class="badge">✨ Deployed with Pulumi</span>
            <span class="badge">📝 Infrastructure as Code</span>
            <span class="badge">🔄 Git Workflow</span>
        </div>

        <div style="text-align: center; margin-top: 30px; opacity: 0.8;">
            <p>🎯 This entire server was created with Python code!</p>
            <p>🚀 Changes deployed automatically via Git push</p>
            <p>💰 Can be destroyed with one command - no surprise bills!</p>
        </div>
    </div>
</body>
</html>
EOF


# cat > /var/www/html/index.html << 'EOF'
# <!DOCTYPE html>
# <html>
# <head>
#     <title>EC2 Instance & Pulumi Info</title>
#     <style>
#         body {{ font-family: Arial; background: #222; color: #eee; padding: 40px; }}
#         .container {{ border: 1px solid #00ff99; padding: 40px; background: #333; border-radius: 12px; margin-bottom: 20px; }}
#         .pulumi-container {{ border: 1px solid #ff6b35; padding: 40px; background: #333; border-radius: 12px; }}
#         h1 {{ color: #00ff99; }}
#         h2 {{ color: #ff6b35; }}
#         h3 {{ color: #ccc; margin-top: 25px; margin-bottom: 10px; border-bottom: 1px solid #555; padding-bottom: 5px; }}
#         .highlight {{ color: #00ff99; font-weight: bold; }}
#         small {{ color: #999; font-style: italic; }}
#     </style>
# </head>
# <body>
#     <!-- EC2 Instance Information -->
#     <div class="container">
#         <h1>🖥️ EC2 Instance Information</h1>
#         <p><b>Instance ID:</b> INSTANCE_ID_PLACEHOLDER</p>
#         <p><b>Instance Type:</b> INSTANCE_TYPE_PLACEHOLDER</p>
#         <p><b>Availability Zone:</b> AVAILABILITY_ZONE_PLACEHOLDER</p>
#         <p><b>Region:</b> REGION_PLACEHOLDER</p>
#     </div>
    
#     <!-- Pulumi Deployment Information -->
#     <div class="pulumi-container">
#         <h2>⚡ Pulumi Deployment Information</h2>
        
#         <h3>1. Project Details</h3>
#         <p><b>Project Name:</b> <span class="highlight">PROJECT_NAME_PLACEHOLDER</span></p>
#         <p><b>Stack:</b> <span class="highlight">STACK_PLACEHOLDER</span></p>
        
#         <h3>2. Resource Naming & Tags</h3>
#         <p><b>AWS Resource Prefix:</b> <span class="highlight">ORG_PLACEHOLDER</span></p>
#         <p><b>Tags Applied:</b></p>
#         <ul>
#             <li><b>Environment:</b> <span class="highlight">ENVIRONMENT_PLACEHOLDER</span></li>
#             <li><b>ManagedBy:</b> <span class="highlight">MANAGED_BY_PLACEHOLDER</span></li>
#             <li><b>GitRepo:</b> <span class="highlight">GIT_REPO_PLACEHOLDER</span></li>
#         </ul>
#         <small>Example: This VPC is named "ORG_PLACEHOLDER-STACK_PLACEHOLDER-PROJECT_NAME_PLACEHOLDER-vpc" and tagged with Environment=ENVIRONMENT_PLACEHOLDER</small>
        
#         <h3>3. Source & Deployment Tracking</h3>
#         <p><b>GitHub Org:</b> <span class="highlight">GITHUB_ORG_PLACEHOLDER</span></p>
#         <p><b>Pulumi Org:</b> <span class="highlight">PULUMI_ORG_PLACEHOLDER</span></p>
#     </div>
# </body>
# </html>
# EOF


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
sed -i "s/GITHUB_ORG_PLACEHOLDER/$GITHUB_ORG/g" /var/www/html/index.html
sed -i "s/PULUMI_ORG_PLACEHOLDER/$PULUMI_ORG/g" /var/www/html/index.html
"""

# --- 5. Create EC2 Instance ---
ec2_instance = aws.ec2.Instance("web-server-instance",
    instance_type="t2.small",
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