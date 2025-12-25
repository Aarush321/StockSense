# Push Code to GitHub - Quick Guide

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. Repository name: `StockSense` (or your choice)
4. Make it **Public** (or Private if you prefer)
5. **DO NOT** initialize with README, .gitignore, or license (we already have files)
6. Click **"Create repository"**

## Step 2: Push Your Code

Run these commands in your terminal:

```bash
cd /Users/aarushravichandran/Desktop/Code/StockAnalysisTool

# Add your GitHub repository as remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Replace:**
- `YOUR_USERNAME` with your GitHub username
- `YOUR_REPO_NAME` with your repository name

## Example:
If your username is `aarush` and repo name is `StockSense`:
```bash
git remote add origin https://github.com/aarush/StockSense.git
git branch -M main
git push -u origin main
```

## If You Need to Authenticate:

If GitHub asks for authentication:
- Use a **Personal Access Token** (not your password)
- Create one at: https://github.com/settings/tokens
- Select scope: `repo`
- Copy the token and use it as the password when pushing

---

## After Pushing:

Once pushed, you can:
1. **Deploy Backend to Render** (see DEPLOYMENT.md)
2. **Deploy Frontend to Netlify** (see DEPLOYMENT.md)

Good luck! 🚀

