# How to Start the App

## Quick Start (No Node.js Required!)

1. **Start the Backend** (Terminal 1):
   ```bash
   cd backend
   python3 app.py
   ```
   You should see: `Running on http://0.0.0.0:5001`

2. **Open the App** (Browser):
   - Simply open `frontend/index-standalone.html` in your web browser
   - Or double-click the file in Finder
   - Or run: `open frontend/index-standalone.html`

That's it! The app is now running and fully functional.

## What's Running

- ✅ **Backend**: Flask server on `http://localhost:5001`
- ✅ **Frontend**: Standalone HTML file (no build step needed!)

## Features Available

- Search for any stock symbol (AAPL, TSLA, GOOGL, etc.)
- View comprehensive analysis:
  - Company overview and current price
  - AI-powered recommendations
  - Social sentiment analysis
  - Professional analyst opinions
  - Recent news articles
- Star/unstar stocks (saved in SQLite database)

## Troubleshooting

**Backend not responding?**
- Make sure port 5001 is not in use
- Check that all Python dependencies are installed: `pip3 list | grep flask`

**Can't connect to backend?**
- Make sure the backend is running: `curl http://localhost:5001/api/health`
- Check browser console for CORS errors (should be handled by flask-cors)

**Want the full React version?**
- Install Node.js from https://nodejs.org/
- Then run: `cd frontend && npm install && npm run dev`

