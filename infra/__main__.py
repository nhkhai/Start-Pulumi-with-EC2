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




# --- 1. Create a Security Group ---
# A security group acts as a virtual firewall for your EC2 instance
# to control inbound and outbound traffic.
# This example allows inbound SSH (port 22) traffic from anywhere (0.0.0.0/0).
# For production, restrict this to known IP addresses.
security_group = aws.ec2.SecurityGroup("web-sg",
    description="Enable SSH access to EC2 instance",
    ingress=[
        # Allow SSH from anywhere
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        # Allow all outbound traffic
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1", # -1 means all protocols
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={
        "Name": f"{org}-{stack}-{project_name}-sg",
    })

# --- 2. Select an Amazon Machine Image (AMI) ---
# We're using a public Amazon Linux 2 AMI.
# You should choose an AMI specific to your region.
# This example finds the latest Amazon Linux 2 AMI for x86_64 architecture.
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        aws.ec2.GetAmiFilterArgs(name="name", values=["amzn2-ami-hvm-*-x86_64-gp2"]),
        aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
    ])

# --- 3. Create an EC2 Instance ---
# This defines the EC2 instance itself.
# `instance_type`: Defines the hardware specifications (e.g., CPU, memory).
# `ami`: The ID of the Amazon Machine Image to use.
# `vpc_security_group_ids`: Associates the instance with our newly created security group.
# `key_name`: (Optional) If you want to SSH into the instance with a key pair,
#             you'll need to specify its name here. Make sure the key pair
#             exists in your AWS account and region.
#             Example: key_name="my-ssh-key"
ec2_instance = aws.ec2.Instance("web-server-instance",
    instance_type="t2.micro",  # A small, cost-effective instance type
    ami=ami.id,
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
