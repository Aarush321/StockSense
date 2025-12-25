# How to Get Reddit API Credentials

## Step-by-Step Guide

### 1. Create a Reddit Account
- If you don't have one, create a Reddit account at https://www.reddit.com/register

### 2. Create a Reddit App
1. Go to **Reddit Apps**: https://www.reddit.com/prefs/apps
2. Scroll down to the bottom of the page
3. Click **"create another app..."** or **"create app"** button

### 3. Fill Out the App Creation Form

**App Details:**
- **Name**: Choose a name (e.g., "Stock Analysis Tool" or "MyStockApp")
- **App type**: Select **"script"** (this is for personal use/scripts)
- **Description**: Optional - describe what your app does (e.g., "Analyzes stock sentiment from Reddit")
- **About URL**: Leave blank or add your website
- **Redirect URI**: Enter `http://localhost:8080` (required but not used for script apps)

### 4. Create the App
- Click **"create app"** button

### 5. Get Your Credentials

After creating the app, you'll see:
- **Client ID**: This is the string under your app name (looks like: `abc123def456ghi789`)
- **Client Secret**: This is the "secret" field (looks like: `xyz789_secret_key_here`)

**Important Notes:**
- The Client ID is visible immediately
- The Client Secret is shown as dots - click "edit" or hover to reveal it
- **Save these immediately** - you won't be able to see the secret again!

### 6. Add to Your .env File

Copy these values to your `backend/.env` file:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

## Reddit API Limitations

- **Rate Limits**: Reddit API has rate limits (typically 60 requests per minute)
- **Read-Only**: For sentiment analysis, you only need read access (no special permissions needed)
- **No OAuth Required**: For read-only public data, you can use "script" app type without full OAuth

## Testing Your Credentials

Once you have the credentials, the app will use them to:
- Search Reddit for stock mentions
- Analyze sentiment from comments and posts
- Aggregate discussion data

## Troubleshooting

**Can't see Client Secret?**
- Click "edit" on your app
- The secret should be visible there
- If you lost it, you'll need to create a new app

**Getting 401/403 errors?**
- Make sure your Client ID and Secret are correct
- Check that you copied them without extra spaces
- Verify the app type is set to "script"

**Rate limit errors?**
- Reddit limits requests per minute
- The code should handle this with retries
- Consider adding delays between requests if needed

