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

Edit `infra/__main__.py` and replace the HTML section (around line 101):
```python
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