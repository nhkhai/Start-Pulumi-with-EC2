#!/bin/bash

echo "--- Starting application setup ---"

# Install Apache web server and AWS CLI v2
yum update -y
yum install -y httpd
yum install -y unzip

# We need the AWS CLI to get the instance name tag
# The Amazon Linux 2 AMI comes with v1, but let's ensure it's there and working
# If you were on another OS, you'd install it here.

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# --- Dynamic Metadata Fetching ---
# Use the Instance Metadata Service (IMDS) for most details
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_TYPE=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/instance-type)
AVAILABILITY_ZONE=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION=$(echo $AVAILABILITY_ZONE | sed 's/.$//')

# Use the AWS CLI to get the 'Name' tag (requires IAM role permission)
# This command finds the tag where the key is 'Name' for the current instance ID
INSTANCE_NAME=$(aws ec2 describe-tags --region $REGION --filters "Name=resource-id,Values=$INSTANCE_ID" "Name=key,Values=Name" --query "Tags[0].Value" --output text)

echo "Instance Name: $INSTANCE_NAME"
echo "Instance ID: $INSTANCE_ID"

# --- Template Processing ---
# Read the template, replace placeholders with our variables, and write the final index.html
sed "s/__INSTANCE_NAME__/$INSTANCE_NAME/g; s/__INSTANCE_ID__/$INSTANCE_ID/g; s/__INSTANCE_TYPE__/$INSTANCE_TYPE/g; s/__AVAILABILITY_ZONE__/$AVAILABILITY_ZONE/g; s/__REGION__/$REGION/g" \
    /app/index.html.template > /var/www/html/index.html

echo "--- Application setup complete ---"