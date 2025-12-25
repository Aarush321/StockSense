# Quick Start Guide

## Prerequisites Check

Before starting, make sure you have:
- Python 3.8+ installed (`python3 --version`)
- Node.js 16+ installed (`node --version`)
- npm installed (`npm --version`)

## Step-by-Step Setup

### 1. Backend Setup (Terminal 1)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
cp env.example .env

# Edit .env and add at least one AI API key:
# ANTHROPIC_API_KEY=your_key_here
# OR
# OPENAI_API_KEY=your_key_here

# Start the server
python app.py
```

You should see: `Running on http://127.0.0.1:5000`

### 2. Frontend Setup (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

You should see: `Local: http://localhost:3000`

### 3. Open in Browser

Open `http://localhost:3000` in your browser.

## Testing the Application

1. **Search for a stock**: Enter "AAPL" (Apple) in the search bar and click "Analyze Stock"
2. **View analysis**: You'll see company info, news, sentiment, analyst opinions, and AI recommendation
3. **Star a stock**: Click the star icon (☆) to save it to your dashboard
4. **View dashboard**: Click the "Dashboard" tab to see all your starred stocks
5. **Auto-refresh**: Enable auto-refresh in the dashboard to keep stocks updated

## Getting API Keys (Optional but Recommended)

### For AI Recommendations:
- **Anthropic (Claude)**: https://console.anthropic.com/
- **OpenAI (GPT-4)**: https://platform.openai.com/api-keys

### For Enhanced Features (Optional):
- **Finnhub** (News): https://finnhub.io/
- **Alpha Vantage** (Stock Data): https://www.alphavantage.co/support/#api-key

## Troubleshooting

### Backend won't start
- Make sure port 5000 is not in use
- Check that all dependencies are installed: `pip list`
- Verify Python version: `python3 --version` (should be 3.8+)

### Frontend won't start
- Make sure port 3000 is not in use
- Check that Node.js is installed: `node --version`
- Try deleting `node_modules` and running `npm install` again

### No AI recommendations showing
- The app works without API keys but shows mock recommendations
- Add `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` to `backend/.env` for real AI analysis
- Restart the backend server after adding keys

### Stock data not loading
- Check your internet connection
- Some stock symbols may not be available
- Try popular symbols like: AAPL, TSLA, GOOGL, MSFT, AMZN

## Next Steps

- Read the full README.md for detailed documentation
- Customize the UI in `frontend/src/components/`
- Add real Reddit/Twitter API integration in `backend/services/stock_service.py`
- Explore the codebase to understand the architecture

