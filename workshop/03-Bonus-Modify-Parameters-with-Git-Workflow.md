# Bonus: Modify EC2 Parameters with Git Workflow

Now let's modify your infrastructure and redeploy using Git workflow. This shows the real power of Infrastructure as Code!

## What We'll Change

1. **Bigger server** - Upgrade from t2.micro to t2.small
2. **Change Pulumi config** - Update region and tags
3. **Deploy via Git** - Push changes to trigger automatic deployment

## Step 1: Upgrade Server Size

Edit `infra/__main__.py` around line 154:

**Change this:**
```python
instance_type="t2.micro",
```

**To this:**
```python
instance_type="t2.small",
```

## Step 2: Update Pulumi Configuration

Edit `infra/Pulumi.dev.yaml` to change region and tags:

**Change this:**
```yaml
config:
  aws:region: ap-southeast-1
  aws:defaultTags:
    tags: 
      Environment: dev 
      ManagedBy: Pulumi
      GitRepo: Start-Pulumi-with-EC2
```

**To this:**
```yaml
config:
  aws:region: us-west-2              # Different region
  aws:defaultTags:
    tags: 
      Environment: workshop          # Updated environment
      ManagedBy: Pulumi
      GitRepo: Start-Pulumi-with-EC2

```

## Step 3: Deploy via Git Workflow

Now deploy your changes using GitHub Actions:

```bash
# Stage your changes
git add infra/__main__.py infra/Pulumi.dev.yaml

# Commit with descriptive message
git commit -m "Upgrade to t2.small and update config"

# Push to dev branch to trigger deployment
git push origin dev
```

## Step 4: Monitor the Deployment

1. Go to your repository's **Actions** tab
2. Watch the **"Deploy EC2 App"** workflow run
3. Pulumi will show what's changing:
   - ⚠️ **Replacing** EC2 instance (new instance type and region)
   - ✅ **Updating** tags

## Step 5: Verify Your Changes

Once deployment completes:

1. **Check the workflow output** for the new web URL
2. **Visit your website** → Notice it's now in the new region
3. **Verify instance type** → Should show "t2.small"
4. **Check AWS Console** → See new tags applied

## More Changes to Try: Make the Webpage More Pretty

Replace the HTML section in `infra/__main__.py` (around line 101 to line 141) with this beautiful version:

```python

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

```
## Step 6: Deploy Another Change

Try making another change and deploy it:

```bash
# Make your changes to config or instance type
git add .
git commit -m "Beauty the webpage"
git push origin dev
```

## Step 7: Clean Up When Done

**Important:** Always destroy when finished!

### Via GitHub Actions:
1. Go to **Actions** tab
2. Click **"Deploy EC2 App"** workflow
3. Click **"Run workflow"**
4. Select **"destroy"** from dropdown
5. Click **"Run workflow"**

### Via Local Command:
```bash
cd infra
pulumi destroy --stack dev
```

## What You Just Learned

🎯 **Key Points:**
- ✅ Modified EC2 instance parameters with code
- ✅ Updated Pulumi configuration (region, tags)
- ✅ Used Git workflow for automated deployment
- ✅ Tracked all changes in version control
- ✅ Safe, predictable infrastructure updates

## Real-World Benefits

This workflow demonstrates how real teams manage infrastructure:

- **Version Control**: All infrastructure changes are tracked
- **Code Reviews**: Team can review infrastructure changes before deployment
- **Automated Testing**: Can add validation steps to the workflow
- **Rollback**: Easy to revert to previous versions
- **Consistency**: Same process for dev, staging, and production

Congratulations! You now understand Infrastructure as Code with Git workflows! 🎉