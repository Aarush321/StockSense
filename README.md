# Stock Analysis Tool

A beginner-friendly stock analysis application that helps users make informed investment decisions by aggregating AI-powered insights, news, social sentiment, and professional opinions.

## Features

- **Stock Search & Analysis**: Comprehensive analysis including company overview, recent news, social sentiment, analyst ratings, and AI-powered recommendations
- **Dashboard**: View and manage your starred stocks with auto-refresh functionality
- **AI Recommendations**: Get beginner-friendly investment advice powered by Claude or OpenAI
- **Social Sentiment**: Aggregate sentiment from Reddit and Twitter
- **Professional Analysis**: Analyst ratings and price targets from major financial institutions

## Tech Stack

- **Backend**: Python with Flask
- **Frontend**: React.js with Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Data Persistence**: SQLite for local storage

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- API keys (optional but recommended):
  - Anthropic API key (for Claude) or OpenAI API key
  - Alpha Vantage API key (optional)
  - Finnhub API key (optional, for news)
  - News API key (optional)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys (at least one AI API key):
```
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here

# Optional
ALPHA_VANTAGE_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

6. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional, defaults to localhost:5000):
```
VITE_API_URL=http://localhost:5000/api
```

4. Run the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. Start both the backend and frontend servers
2. Open your browser to `http://localhost:3000`
3. Enter a stock symbol (e.g., AAPL, TSLA, GOOGL) in the search bar
4. View comprehensive analysis including:
   - Company overview and current price
   - Recent news articles
   - Social media sentiment
   - Professional analyst opinions
   - AI-powered recommendation
5. Click the star icon to save stocks to your dashboard
6. View all starred stocks in the Dashboard tab
7. Enable auto-refresh to keep your starred stocks updated

## API Endpoints

- `POST /api/analyze` - Analyze a stock symbol
- `GET /api/starred` - Get all starred stocks
- `POST /api/star` - Add a stock to starred list
- `DELETE /api/star/<symbol>` - Remove a stock from starred list
- `GET /api/refresh/<symbol>` - Refresh data for a specific stock
- `GET /api/health` - Health check endpoint

## Project Structure

```
StockAnalysisTool/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── database/
│   │   └── db.py             # SQLite database operations
│   └── services/
│       ├── stock_service.py  # Stock data fetching
│       └── ai_service.py     # AI recommendation generation
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── context/          # React Context for state
│   │   ├── services/         # API service layer
│   │   └── App.jsx           # Main app component
│   └── package.json
└── README.md
```

## Notes

- The application uses `yfinance` as the primary data source, which doesn't require API keys
- Social sentiment currently uses mock data. To integrate real Reddit/Twitter APIs, update `stock_service.py`
- AI recommendations work best with either Anthropic or OpenAI API keys. Without them, mock recommendations are provided
- The SQLite database is automatically created in `backend/database/stocks.db`

## Future Enhancements

- Historical price charts
- Compare multiple stocks side-by-side
- Email alerts for significant changes
- Portfolio tracking
- Dark mode toggle
- Real Reddit and Twitter API integration

## License

MIT

