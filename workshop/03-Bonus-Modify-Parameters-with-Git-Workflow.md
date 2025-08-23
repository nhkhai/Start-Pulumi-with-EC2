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
```

**To this:**
```yaml
config:
  aws:region: us-west-2              # Different region
  aws:defaultTags:
    tags: 
      Environment: workshop          # Updated environment

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

Edit `infra/__main__.py` and replace the HTML section (around line 82):

```python
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>🚀 My Awesome Pulumi Server</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 0;
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            padding: 50px; 
            border-radius: 25px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 700px;
            animation: fadeIn 1s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 { 
            color: #00ff99; 
            font-size: 3em;
            margin-bottom: 30px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 3px 3px 6px rgba(0,0,0,0.5), 0 0 20px #00ff99; }
            to { text-shadow: 3px 3px 6px rgba(0,0,0,0.5), 0 0 30px #00ff99, 0 0 40px #00ff99; }
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .info-card {
            background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .info-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,255,153,0.2);
        }
        .info-label {
            font-weight: bold;
            color: #00ff99;
            font-size: 1.2em;
            margin-bottom: 8px;
        }
        .info-value {
            font-size: 1.1em;
            word-break: break-all;
            opacity: 0.9;
        }
        .badges {
            margin: 40px 0;
        }
        .badge {
            display: inline-block;
            background: linear-gradient(45deg, #00ff99, #00cc7a);
            color: #222;
            padding: 12px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin: 8px;
            box-shadow: 0 5px 15px rgba(0,255,153,0.3);
            transition: transform 0.2s ease;
        }
        .badge:hover {
            transform: scale(1.05);
        }
        .footer {
            margin-top: 40px;
            font-style: italic;
            opacity: 0.8;
            font-size: 1.1em;
        }
        .emoji {
            font-size: 1.5em;
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 My Awesome Pulumi Server</h1>
        
        <div class="info-grid">
            <div class="info-card">
                <div class="info-label">🆔 Instance ID</div>
                <div class="info-value">INSTANCE_ID_PLACEHOLDER</div>
            </div>
            <div class="info-card">
                <div class="info-label">💻 Server Type</div>
                <div class="info-value">INSTANCE_TYPE_PLACEHOLDER</div>
            </div>
            <div class="info-card">
                <div class="info-label">📍 Location</div>
                <div class="info-value">AVAILABILITY_ZONE_PLACEHOLDER</div>
            </div>
            <div class="info-card">
                <div class="info-label">🌎 Region</div>
                <div class="info-value">REGION_PLACEHOLDER</div>
            </div>
        </div>

        <div class="badges">
            <span class="badge">✨ Deployed with Pulumi</span>
            <span class="badge">📝 Infrastructure as Code</span>
            <span class="badge">🔄 Git Workflow</span>
        </div>

        <div class="footer">
            <p><span class="emoji">🎯</span> This entire server was created with Python code!</p>
            <p><span class="emoji">🚀</span> Changes deployed automatically via Git push</p>
            <p><span class="emoji">💰</span> Can be destroyed with one command - no surprise bills!</p>
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