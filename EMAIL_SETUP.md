# Email Service Configuration Guide

This guide will help you configure email service for password reset and email verification.

## Quick Setup Options

### Option 1: SendGrid (Recommended - Easiest)

**Step 1: Sign up for SendGrid**
1. Go to https://sendgrid.com
2. Sign up for a free account (100 emails/day free)
3. Complete email verification

**Step 2: Verify Sender Email**
1. In SendGrid dashboard, go to **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in your email details (e.g., `noreply@yourdomain.com` or use your personal email)
4. Check your email and click the verification link
5. **Note the verified email address** - you'll need it for `FROM_EMAIL`

**Step 3: Create API Key**
1. Go to **Settings** → **API Keys**
2. Click **Create API Key**
3. Name it (e.g., "StockSense")
4. Select **Full Access** (or just "Mail Send" permissions)
5. Click **Create & View**
6. **Copy the API key immediately** (you won't see it again!)

**Step 4: Add to Render**
1. Go to https://dashboard.render.com
2. Click on your backend service
3. Go to **Environment** tab
4. Add these variables:

```
SENDGRID_API_KEY = [paste your API key here]
FROM_EMAIL = [the email you verified in SendGrid, e.g., noreply@yourdomain.com]
FRONTEND_URL = https://your-netlify-url.netlify.app
```

**Step 5: Redeploy**
- Go to your Render service → **Manual Deploy** → **Deploy latest commit**

---

### Option 2: SMTP (Gmail Example)

**Step 1: Enable 2-Factor Authentication**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not already enabled

**Step 2: Create App Password**
1. Go to https://myaccount.google.com/apppasswords
2. Select **Mail** and your device
3. Click **Generate**
4. **Copy the 16-character password** (you'll need this)

**Step 3: Add to Render**
1. Go to https://dashboard.render.com
2. Click on your backend service
3. Go to **Environment** tab
4. Add these variables:

```
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
SMTP_USER = your-email@gmail.com
SMTP_PASSWORD = [paste the 16-character app password]
FROM_EMAIL = your-email@gmail.com
FRONTEND_URL = https://your-netlify-url.netlify.app
```

**Step 4: Redeploy**
- Go to your Render service → **Manual Deploy** → **Deploy latest commit**

---

## Other Email Providers (SMTP)

### Outlook/Hotmail
```
SMTP_HOST = smtp-mail.outlook.com
SMTP_PORT = 587
SMTP_USER = your-email@outlook.com
SMTP_PASSWORD = [your password or app password]
FROM_EMAIL = your-email@outlook.com
```

### Yahoo
```
SMTP_HOST = smtp.mail.yahoo.com
SMTP_PORT = 587
SMTP_USER = your-email@yahoo.com
SMTP_PASSWORD = [your app password]
FROM_EMAIL = your-email@yahoo.com
```

---

## Testing

After configuration:
1. Try the "Forgot Password" feature
2. Check Render logs for email sending status
3. Look for these messages:
   - ✅ `Password reset email sent successfully to {email}` = Working!
   - ❌ `Email service not configured` = Check your environment variables

---

## Troubleshooting

**Emails not sending?**
- Check Render logs for error messages
- Verify all environment variables are set correctly
- For SendGrid: Make sure sender email is verified
- For SMTP: Make sure you're using an app password, not your regular password

**Verification links not working?**
- Make sure `FRONTEND_URL` matches your Netlify URL exactly
- Check that the URL doesn't have a trailing slash

**Still having issues?**
- Check the Render logs when someone requests a password reset
- The logs will show exactly what's wrong with the email service

