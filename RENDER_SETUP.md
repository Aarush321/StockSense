# Render Environment Variables Setup Guide

This guide will help you configure the email service and other environment variables on Render.

## Step 1: Get Your Netlify URL

1. Go to your Netlify dashboard
2. Find your site URL (e.g., `https://your-site-name.netlify.app`)
3. Copy this URL - you'll need it for `FRONTEND_URL`

## Step 2: Choose Email Service

### Option A: SendGrid (Recommended - Free tier available)

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Go to Settings → API Keys
3. Create a new API key with "Full Access" or "Mail Send" permissions
4. Copy the API key

### Option B: SMTP (Gmail, Outlook, etc.)

For Gmail:
1. Enable 2-Factor Authentication
2. Go to Google Account → Security → App Passwords
3. Create an app password for "Mail"
4. Use these settings:
   - SMTP_HOST: `smtp.gmail.com`
   - SMTP_PORT: `587`
   - SMTP_USER: Your Gmail address
   - SMTP_PASSWORD: The app password you created

## Step 3: Configure Render Environment Variables

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your backend service (StockSense backend)
3. Go to the "Environment" tab
4. Click "Add Environment Variable" and add the following:

### Required Variables:

```
JWT_SECRET_KEY
```
- Value: Generate a random string (e.g., use: `openssl rand -hex 32`)
- This secures your JWT tokens

```
ALLOWED_ORIGINS
```
- Value: `http://localhost:3000,http://localhost:5000,http://127.0.0.1:5000,http://localhost:5001,https://YOUR-NETLIFY-URL.netlify.app`
- Replace `YOUR-NETLIFY-URL` with your actual Netlify URL

```
FRONTEND_URL
```
- Value: `https://YOUR-NETLIFY-URL.netlify.app`
- Replace `YOUR-NETLIFY-URL` with your actual Netlify URL

### Email Service Variables (Choose ONE):

**If using SendGrid:**
```
SENDGRID_API_KEY
```
- Value: Your SendGrid API key

```
FROM_EMAIL
```
- Value: The email address you verified in SendGrid (e.g., `noreply@yourdomain.com`)

**OR if using SMTP:**
```
SMTP_HOST
```
- Value: `smtp.gmail.com` (or your email provider's SMTP host)

```
SMTP_PORT
```
- Value: `587` (for TLS) or `465` (for SSL)

```
SMTP_USER
```
- Value: Your email address

```
SMTP_PASSWORD
```
- Value: Your email app password

```
FROM_EMAIL
```
- Value: Your email address

## Step 4: Redeploy Backend

After adding all environment variables:

1. Go to your Render service dashboard
2. Click "Manual Deploy" → "Deploy latest commit"
3. Wait for deployment to complete (2-5 minutes)

## Step 5: Verify Setup

1. Try signing up a new account
2. Check your email for verification email
3. If emails aren't sending, check Render logs for errors

## Troubleshooting

- **Emails not sending**: Check Render logs for email service errors
- **Verification links not working**: Make sure `FRONTEND_URL` matches your Netlify URL exactly
- **CORS errors**: Make sure your Netlify URL is in `ALLOWED_ORIGINS`

## Notes

- If no email service is configured, the app will still work but emails won't be sent
- Verification emails will be logged to console in development mode
- SendGrid free tier: 100 emails/day (perfect for testing and small scale)

