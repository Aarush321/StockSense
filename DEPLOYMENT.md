# Deployment Guide: StockSense

This guide will help you deploy StockSense to production:
- **Frontend**: Netlify
- **Backend**: Render

## Prerequisites

1. GitHub account (recommended) or Git repository
2. Netlify account (free tier works)
3. Render account (free tier works)
4. Your API keys ready

---

## Step 1: Deploy Backend to Render

### 1.1 Prepare Your Repository

1. Make sure your code is in a Git repository (GitHub recommended)
2. Push all changes to your repository

### 1.2 Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (or use "Public Git repository")
4. Configure the service:
   - **Name**: `stocksense-backend` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Root Directory**: `backend`

### 1.3 Add Environment Variables in Render

Go to **Environment** tab and add these variables:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here
NEWS_API_KEY=your_news_api_key_here
ALLOWED_ORIGINS=https://your-netlify-site.netlify.app
PYTHON_VERSION=3.9.18
```

**Important**: 
- Replace `your_netlify_site.netlify.app` with your actual Netlify URL (you'll get this after Step 2)
- You can update `ALLOWED_ORIGINS` later after deploying frontend

### 1.4 Deploy

1. Click **"Create Web Service"**
2. Wait for deployment to complete (usually 2-5 minutes)
3. **Copy your backend URL** (e.g., `https://stocksense-backend.onrender.com`)

---

## Step 2: Deploy Frontend to Netlify

### 2.1 Update Frontend for Production

1. Before deploying, you need to inject the backend URL into the HTML
2. We'll use Netlify's build-time environment variables

### 2.2 Method 1: Using Netlify's Build Plugins (Recommended)

1. Create a simple build script that injects the API URL:

```bash
# Create a build script (optional - we'll use Netlify's rewrite instead)
```

### 2.3 Method 2: Manual Update (Quick Start)

1. Update `frontend/index-standalone.html` line 41:
   ```javascript
   const API_BASE = 'https://your-backend-url.onrender.com/api';
   ```
   Replace `your-backend-url.onrender.com` with your actual Render URL

2. Commit and push to Git

### 2.4 Deploy to Netlify

1. Go to [Netlify Dashboard](https://app.netlify.com/)
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect your GitHub repository
4. Configure build settings:
   - **Base directory**: `frontend`
   - **Publish directory**: `frontend`
   - **Build command**: (leave empty - no build needed)

5. Add Environment Variable:
   - Go to **Site settings** → **Environment variables**
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.onrender.com/api`

6. However, since we're using static HTML, we need a different approach...

### 2.5 Update Frontend Code for Netlify

Since Netlify serves static HTML, we need to update the HTML file directly:

1. In your `frontend/index-standalone.html`, replace line 41 with:
   ```javascript
   const API_BASE = (() => {
       // Check if we're in production (Netlify)
       if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
           return 'https://your-backend-url.onrender.com/api';
       }
       return 'http://localhost:5001/api';
   })();
   ```

2. Replace `your-backend-url.onrender.com` with your actual Render URL

3. Commit and push changes

4. Netlify will auto-deploy

### 2.6 Update CORS in Render

1. Go back to Render dashboard
2. Update the `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-site-name.netlify.app
   ```
3. Redeploy the backend service

---

## Step 3: Verify Deployment

### 3.1 Test Backend

Visit: `https://your-backend-url.onrender.com/api/health`

Should return: `{"status": "healthy"}`

### 3.2 Test Frontend

1. Visit your Netlify URL
2. Try searching for a stock (e.g., "AAPL")
3. Verify the API calls work

---

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:
1. Make sure `ALLOWED_ORIGINS` in Render includes your Netlify URL
2. Format: `https://your-site.netlify.app` (no trailing slash)
3. Redeploy backend after updating

### API Not Working

1. Check browser console for errors
2. Verify backend URL is correct in `index-standalone.html`
3. Check Render logs for backend errors
4. Verify all API keys are set in Render environment variables

### Backend Not Starting

1. Check Render logs
2. Verify `requirements.txt` includes `gunicorn`
3. Make sure start command is: `gunicorn app:app`

---

## Updating requirements.txt

Make sure `gunicorn` is in your requirements.txt for production:

```
flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
requests==2.31.0
yfinance==0.2.28
anthropic==0.18.1
openai==1.12.0
gunicorn==21.2.0
```

---

## Cost Considerations

### Netlify (Free Tier)
- ✅ Free hosting for static sites
- ✅ 100GB bandwidth/month
- ✅ SSL included

### Render (Free Tier)
- ⚠️ Free tier services **spin down after 15 minutes of inactivity**
- ⚠️ First request after spin-down takes ~30 seconds to wake up
- 💰 For production use, consider paid tier ($7/month) for always-on service

---

## Quick Reference

- **Backend URL**: `https://your-backend.onrender.com`
- **Frontend URL**: `https://your-site.netlify.app`
- **Backend Health Check**: `https://your-backend.onrender.com/api/health`

Good luck with your deployment! 🚀

