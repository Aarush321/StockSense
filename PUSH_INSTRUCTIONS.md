# Push to GitHub - Authentication Required

Your code is ready to push, but GitHub requires authentication. Here are your options:

## Option 1: Use Personal Access Token (Recommended)

1. **Create a Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - Name it: `StockSense Push`
   - Select scope: **`repo`** (full control of private repositories)
   - Click **"Generate token"**
   - **COPY THE TOKEN** (you won't see it again!)

2. **Push using the token:**
   ```bash
   cd /Users/aarushravichandran/Desktop/Code/StockAnalysisTool
   git push -u origin main
   ```
   - When prompted for **Username**: Enter `Aarush321`
   - When prompted for **Password**: Paste your **Personal Access Token** (not your GitHub password)

## Option 2: Use SSH (More Secure)

1. **Check if you have SSH keys:**
   ```bash
   ls -la ~/.ssh/id_*.pub
   ```

2. **If no SSH key exists, create one:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter to accept default location
   # Press Enter twice for no passphrase (or set one)
   ```

3. **Add SSH key to GitHub:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Copy the output
   ```
   - Go to: https://github.com/settings/keys
   - Click **"New SSH key"**
   - Paste your public key
   - Click **"Add SSH key"**

4. **Change remote to SSH:**
   ```bash
   cd /Users/aarushravichandran/Desktop/Code/StockAnalysisTool
   git remote set-url origin git@github.com:Aarush321/StockSense.git
   git push -u origin main
   ```

## Option 3: Use GitHub Desktop App

1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. Add the repository
4. Push from the app

---

## Quick Push (After Authentication Setup)

Once you've set up authentication (Option 1 or 2), run:

```bash
cd /Users/aarushravichandran/Desktop/Code/StockAnalysisTool
git push -u origin main
```

Your code will be pushed to: https://github.com/Aarush321/StockSense

