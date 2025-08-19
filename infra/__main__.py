import pulumi
import pulumi_aws as aws

# --- Configuration ---
# You can set your desired AWS region in your Pulumi stack configuration,
# for example: `pulumi config set aws:region us-east-1`
# Or directly in the code, though stack config is generally preferred.

stack = pulumi.get_stack() # from git action
project_name = pulumi.get_project() # from dev 

config = pulumi.Config('ll-config')
org = config.require('org')

# Using pulumi.export for clarity on outputs
pulumi.export('project_name', project_name)
pulumi.export('stack', stack)


# --- 1. Create a new VPC ---
# This creates a dedicated virtual network for your resources.
vpc = aws.ec2.Vpc("app-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True, # Recommended for many use cases
    tags={
        "Name": f"{org}-{stack}-{project_name}-vpc",
    })

# --- 2. Create an Internet Gateway ---
# This allows communication between your VPC and the internet.
internet_gateway = aws.ec2.InternetGateway("app-igw",
    vpc_id=vpc.id,
    tags={
        "Name": f"{org}-{stack}-{project_name}-igw",
    })

# --- 3. Create a Route Table ---
# This defines rules for directing network traffic from your subnets.
route_table = aws.ec2.RouteTable("app-rt",
    vpc_id=vpc.id,
    routes=[
        # This route sends all traffic destined for outside the VPC (0.0.0.0/0)
        # to the Internet Gateway.
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.id,
        ),
    ],
    tags={
        "Name": f"{org}-{stack}-{project_name}-rt",
    })

# --- 4. Create a Subnet ---
# An EC2 instance must be launched into a subnet.
subnet = aws.ec2.Subnet("app-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",  # A smaller range within the VPC's CIDR block
    map_public_ip_on_launch=True, # Automatically assign a public IP to instances
    tags={
        "Name": f"{org}-{stack}-{project_name}-subnet",
    })

# --- 5. Associate the Route Table with the Subnet ---
# This connects your subnet to the internet via the route table and internet gateway.
route_table_association = aws.ec2.RouteTableAssociation("app-rta",
    subnet_id=subnet.id,
    route_table_id=route_table.id)

# --- 6. Create a Security Group ---
# Acts as a virtual firewall for your EC2 instance.
security_group = aws.ec2.SecurityGroup("web-sg",
    description="Enable HTTP and SSH access to EC2 instance",
    vpc_id=vpc.id,  # <-- Associate with your new VPC
    ingress=[
        # Allow SSH from anywhere (for development)
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            description="Allow SSH access",
        ),
        # Allow HTTP from anywhere
        aws.ec2.SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            description="Allow HTTP access",
        ),
    ],
    egress=[
        # Allow all outbound traffic
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={
        "Name": f"{org}-{stack}-{project_name}-security-group",
    })

# --- 7. Select an Amazon Machine Image (AMI) ---
# Finds the latest Amazon Linux 2 AMI for the current region.
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        aws.ec2.GetAmiFilterArgs(name="name", values=["amzn2-ami-hvm-*-x86_64-gp2"]),
        aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
    ])

# --- 8. Create an EC2 Instance ---
# This defines the EC2 instance itself.
ec2_instance = aws.ec2.Instance("web-server-instance",
    instance_type="t2.micro",
    ami=ami.id,
    # ** THE FIX: Specify the subnet ID for the instance **
    subnet_id=subnet.id,
    vpc_security_group_ids=[security_group.id], # Attach our security group
    tags={
        "Name": f"{org}-{stack}-{project_name}-instance",
    })



# --- Outputs ---
# These outputs provide information about the deployed resources
# once the Pulumi program runs successfully.
pulumi.export("instance_id", ec2_instance.id)
pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("public_dns", ec2_instance.public_dns)
pulumi.export("security_group_id", security_group.id)
