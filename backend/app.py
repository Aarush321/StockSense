from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError
from services.stock_service import StockService
from services.ai_service import AIService
from database.db import init_db, get_starred_stocks, add_starred_stock, remove_starred_stock

# Load .env file from the backend directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Configure CORS for production (allow Netlify domain)
# Update ALLOWED_ORIGINS in Render environment variables with your Netlify URL
allowed_origins_str = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000,http://127.0.0.1:5000,http://localhost:5001')
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',') if origin.strip()]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

# Initialize database
init_db()

# Initialize services
stock_service = StockService()
ai_service = AIService()

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """Main analysis endpoint - optimized for speed"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        # Fetch data sequentially with delays to avoid Yahoo Finance rate limiting
        # Company data first (needed for AI)
        try:
            company_data = stock_service.get_company_overview(symbol)
        except Exception as e:
            print(f"Company overview error: {e}")
            company_data = {}
        
        # Then fetch other data in parallel (but with fewer workers to reduce rate limits)
        with ThreadPoolExecutor(max_workers=2) as executor:  # Reduced from 4 to 2
            news_future = executor.submit(stock_service.get_recent_news, symbol)
            sentiment_future = executor.submit(stock_service.get_social_sentiment, symbol)
            analyst_future = executor.submit(stock_service.get_analyst_ratings, symbol)
            
            # Get other data with reasonable timeouts (these need more time for multiple API calls)
            try:
                news_data = news_future.result(timeout=5)  # Increased from 1.5 to 5 seconds
            except FutureTimeoutError:
                print(f"News data timeout for {symbol}")
                news_data = []
            except Exception as e:
                print(f"News data error for {symbol}: {e}")
                news_data = []
            
            try:
                sentiment_data = sentiment_future.result(timeout=5)  # Increased from 1.5 to 5 seconds
            except FutureTimeoutError:
                print(f"Sentiment data timeout for {symbol}")
                sentiment_data = {}  # Social sentiment has fallbacks, so return empty dict
            except Exception as e:
                print(f"Sentiment data error for {symbol}: {e}")
                sentiment_data = {}  # Will use fallback sentiment
            
            try:
                analyst_data = analyst_future.result(timeout=5)  # Increased from 1.5 to 5 seconds
            except FutureTimeoutError:
                print(f"Analyst data timeout for {symbol}")
                analyst_data = {}
            except Exception as e:
                print(f"Analyst data error for {symbol}: {e}")
                analyst_data = {}
        
        # Generate AI recommendation with 3-second timeout (start immediately after company data)
        # Total target: 3s company + 3s AI = 6s, with 1s buffer for other data
        try:
            ai_recommendation = ai_service.generate_recommendation(
                symbol=symbol,
                company_data=company_data,
                news_data=news_data,
                sentiment_data=sentiment_data,
                analyst_data=analyst_data
            )
        except Exception as e:
            # Fallback to mock recommendation if AI errors
            print(f"AI recommendation error, using mock: {e}")
            ai_recommendation = ai_service._get_mock_recommendation(symbol, company_data, analyst_data, news_data if isinstance(news_data, list) else [])
        
        # Combine all data
        analysis = {
            'symbol': symbol,
            'company': company_data,
            'news': news_data,
            'sentiment': sentiment_data,
            'analyst': analyst_data,
            'ai_recommendation': ai_recommendation
        }
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/starred', methods=['GET'])
def get_starred():
    """Get all starred stocks"""
    try:
        starred = get_starred_stocks()
        return jsonify(starred), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/star', methods=['POST'])
def star_stock():
    """Add stock to starred list"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        add_starred_stock(symbol)
        return jsonify({'message': f'{symbol} added to starred stocks'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/star/<symbol>', methods=['DELETE'])
def unstar_stock(symbol):
    """Remove stock from starred list"""
    try:
        symbol = symbol.upper().strip()
        remove_starred_stock(symbol)
        return jsonify({'message': f'{symbol} removed from starred stocks'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh/<symbol>', methods=['GET'])
def refresh_stock(symbol):
    """Refresh data for a specific saved stock"""
    try:
        symbol = symbol.upper().strip()
        
        # Fetch fresh data (same as analyze endpoint)
        company_data = stock_service.get_company_overview(symbol)
        news_data = stock_service.get_recent_news(symbol)
        sentiment_data = stock_service.get_social_sentiment(symbol)
        analyst_data = stock_service.get_analyst_ratings(symbol)
        
        ai_recommendation = ai_service.generate_recommendation(
            symbol=symbol,
            company_data=company_data,
            news_data=news_data,
            sentiment_data=sentiment_data,
            analyst_data=analyst_data
        )
        
        analysis = {
            'symbol': symbol,
            'company': company_data,
            'news': news_data,
            'sentiment': sentiment_data,
            'analyst': analyst_data,
            'ai_recommendation': ai_recommendation
        }
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-news', methods=['GET'])
def get_market_news():
    """Get general stock market news for today"""
    try:
        news_data = stock_service.get_market_news(limit=10)
        return jsonify(news_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """AI Chatbot endpoint for financial education"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
            
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get recent market news for context (with timeout to prevent hanging)
        market_news = []
        try:
            market_news = stock_service.get_market_news(limit=5)
        except Exception as news_error:
            print(f"Warning: Could not fetch market news: {news_error}")
            market_news = []
        
        # Generate chatbot response
        try:
            response_text = ai_service.chat(message, market_news)
            return jsonify({'response': response_text}), 200
        except Exception as chat_error:
            print(f"Chat error: {chat_error}")
            # Return a helpful error message without printing traceback (avoids broken pipe)
            return jsonify({'error': f'Failed to generate response. Please try again.'}), 500
        
    except Exception as e:
        print(f"Chatbot endpoint error: {e}")
        return jsonify({'error': 'An error occurred processing your request. Please try again.'}), 500

@app.route('/api/price/<symbol>', methods=['GET'])
def get_stock_price(symbol):
    """Lightweight endpoint to get just price and change percentage"""
    try:
        symbol = symbol.upper().strip()
        company_data = stock_service.get_company_overview(symbol)
        
        # Return only essential price data
        price_data = {
            'symbol': symbol,
            'name': company_data.get('name', symbol),
            'currentPrice': company_data.get('currentPrice', 0),
            'changePercent': company_data.get('changePercent', 0)
        }
        
        return jsonify(price_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prices', methods=['POST'])
def get_multiple_prices():
    """Get prices for multiple stocks at once"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols or not isinstance(symbols, list):
            return jsonify({'error': 'List of symbols is required'}), 400
        
        results = {}
        for symbol in symbols:
            try:
                symbol = symbol.upper().strip()
                company_data = stock_service.get_company_overview(symbol)
                results[symbol] = {
                    'symbol': symbol,
                    'name': company_data.get('name', symbol),
                    'currentPrice': company_data.get('currentPrice', 0),
                    'changePercent': company_data.get('changePercent', 0)
                }
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')

