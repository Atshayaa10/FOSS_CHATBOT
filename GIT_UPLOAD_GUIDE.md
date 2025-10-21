# Quick Git Upload Guide

## Step 1: Initialize Git (if not already done)
```powershell
cd "C:\Users\Aradhana S\OneDrive\Documents\chatbotnew"
git init
```

## Step 2: Add your existing GitHub repository as remote
```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Or if you're using SSH:
```powershell
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
```

## Step 3: Check .env file is protected
Make sure your .env file won't be uploaded (already in .gitignore):
```powershell
git status
```
You should NOT see .env in the list!

## Step 4: Add all files
```powershell
git add .
```

## Step 5: Commit your changes
```powershell
git commit -m "Add FOSS-CIT AI Chatbot with OpenRouter and Pinecone"
```

## Step 6: Pull existing changes (if any)
```powershell
git pull origin main --rebase
```
Or if your branch is called master:
```powershell
git pull origin master --rebase
```

## Step 7: Push to GitHub
```powershell
git push -u origin main
```
Or for master branch:
```powershell
git push -u origin master
```

## Important Notes:

✅ Your .env file is protected by .gitignore
✅ Your venv folder won't be uploaded
✅ API keys will remain private

## If repository has existing files:

If you want to merge with existing content:
```powershell
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## Create .env.example for others:

Share what environment variables are needed without exposing your keys:
```powershell
# Already created - see .env file structure in README.md
```
