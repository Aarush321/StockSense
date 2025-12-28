from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError
from services.stock_service import StockService
from services.ai_service import AIService
from database.db import (
    init_db, get_starred_stocks, add_starred_stock, remove_starred_stock,
    create_user, get_user_by_email, get_user_by_id, update_last_login, get_user_count,
    update_user_verification_token, verify_user_email, get_user_by_verification_token,
    set_password_reset_token, get_user_by_reset_token, reset_user_password,
    update_user_profile, get_all_users
)
from services.email_service import EmailService

# Load .env file from the backend directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# JWT secret key (use environment variable in production)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

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
email_service = EmailService()

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
    """Get all starred stocks for the authenticated user"""
    try:
        # Get token from Authorization header or request body
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.args.get('token', '')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        starred = get_starred_stocks(user_id)
        return jsonify(starred), 200
    except Exception as e:
        print(f"Error getting starred stocks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/star', methods=['POST'])
def star_stock():
    """Add stock to starred list for the authenticated user"""
    try:
        # Get token from Authorization header or request body
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.get_json().get('token', '') if request.is_json else ''
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        add_starred_stock(user_id, symbol)
        return jsonify({'message': f'{symbol} added to starred stocks'}), 200
    except Exception as e:
        print(f"Error starring stock: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/star/<symbol>', methods=['DELETE'])
def unstar_stock(symbol):
    """Remove stock from starred list for the authenticated user"""
    try:
        # Get token from Authorization header or request body
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.args.get('token', '')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        symbol = symbol.upper().strip()
        remove_starred_stock(user_id, symbol)
        return jsonify({'message': f'{symbol} removed from starred stocks'}), 200
    except Exception as e:
        print(f"Error unstarring stock: {e}")
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

# Authentication helper functions
def generate_token(user_id, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password (at least 6 characters)"""
    return len(password) >= 6

# Authentication endpoints
@app.route('/api/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = create_user(email, password_hash)
        
        if not user_id:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        update_user_verification_token(user_id, verification_token)
        
        # Send verification email
        try:
            email_service.send_verification_email(email, verification_token)
        except Exception as e:
            print(f"Failed to send verification email: {e}")
            # Continue anyway - user can request resend later
        
        # Generate auth token
        token = generate_token(user_id, email)
        
        # Get user data
        user_data = get_user_by_id(user_id)
        
        return jsonify({
            'message': 'User created successfully. Please check your email to verify your account.',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'email_verified': bool(user_data.get('email_verified', 0)),
                'name': user_data.get('name')
            }
        }), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': 'An error occurred during signup'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        update_last_login(user['id'])
        
        # Generate token
        token = generate_token(user['id'], user['email'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'email_verified': bool(user.get('email_verified', 0)),
                'name': user.get('name')
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint (client-side token removal)"""
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/user-count', methods=['GET'])
def user_count():
    """Get total number of registered users"""
    try:
        count = get_user_count()
        return jsonify({'userCount': count}), 200
    except Exception as e:
        print(f"User count error: {e}")
        return jsonify({'error': 'Failed to get user count'}), 500

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    """Get all registered users (admin endpoint)"""
    try:
        users = get_all_users()
        # Return only safe user data (no password hashes)
        user_list = []
        for user in users:
            user_list.append({
                'id': user.get('id'),
                'email': user.get('email'),
                'name': user.get('name'),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login'),
                'email_verified': bool(user.get('email_verified', 0))
            })
        return jsonify({'users': user_list, 'count': len(user_list)}), 200
    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-token', methods=['POST'])
def verify_user_token():
    """Verify if a token is valid"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        if not token:
            return jsonify({'valid': False}), 200
        
        payload = verify_token(token)
        if payload:
            user_id = payload.get('user_id')
            user_data = get_user_by_id(user_id)
            if user_data:
                return jsonify({
                    'valid': True,
                    'user': {
                        'id': user_id,
                        'email': payload.get('email'),
                        'email_verified': bool(user_data.get('email_verified', 0)),
                        'name': user_data.get('name')
                    }
                }), 200
        return jsonify({'valid': False}), 200
            
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({'valid': False}), 200

# Email verification endpoints
@app.route('/api/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        if not token:
            return jsonify({'error': 'Verification token is required'}), 400
        
        user = get_user_by_verification_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired verification token'}), 400
        
        if user.get('email_verified'):
            return jsonify({'message': 'Email already verified'}), 200
        
        verify_user_email(user['id'])
        
        return jsonify({'message': 'Email verified successfully'}), 200
        
    except Exception as e:
        print(f"Email verification error: {e}")
        return jsonify({'error': 'Failed to verify email'}), 500

@app.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    try:
        data = request.get_json()
        token = data.get('token', '')  # Auth token
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.get('email_verified'):
            return jsonify({'message': 'Email already verified'}), 200
        
        # Generate new verification token
        verification_token = secrets.token_urlsafe(32)
        update_user_verification_token(user_id, verification_token)
        
        # Send verification email
        email_sent = email_service.send_verification_email(user['email'], verification_token)
        
        if email_sent:
            return jsonify({'message': 'Verification email sent'}), 200
        else:
            return jsonify({'error': 'Failed to send verification email. Please check email service configuration.'}), 500
        
    except Exception as e:
        print(f"Resend verification error: {e}")
        return jsonify({'error': 'Failed to resend verification email'}), 500

# Password reset endpoints
@app.route('/api/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request password reset email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = get_user_by_email(email)
        if not user:
            # Don't reveal if email exists for security
            return jsonify({'message': 'If an account exists with this email, a password reset link has been sent'}), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        set_password_reset_token(email, reset_token, expires_at)
        
        # Send reset email
        email_sent = email_service.send_password_reset_email(email, reset_token)
        
        if email_sent:
            return jsonify({'message': 'If an account exists with this email, a password reset link has been sent'}), 200
        else:
            return jsonify({'error': 'Failed to send reset email. Please check email service configuration.'}), 500
        
    except Exception as e:
        print(f"Password reset request error: {e}")
        return jsonify({'error': 'Failed to process password reset request'}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        new_password = data.get('password', '')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and password are required'}), 400
        
        if not validate_password(new_password):
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        user = get_user_by_reset_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Check if token expired
        expires_at = user.get('reset_token_expires')
        if expires_at:
            expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.utcnow() > expires_datetime.replace(tzinfo=None):
                return jsonify({'error': 'Reset token has expired'}), 400
        
        # Reset password
        password_hash = generate_password_hash(new_password)
        reset_user_password(user['id'], password_hash)
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({'error': 'Failed to reset password'}), 500

# User profile endpoints
@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.get_json().get('token', '') if request.is_json else ''
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'email_verified': bool(user.get('email_verified', 0)),
                'name': user.get('name'),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login')
            }
        }), 200
        
    except Exception as e:
        print(f"Get profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or data.get('token', '')
        name = data.get('name', '').strip()
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        
        # Update profile
        update_user_profile(user_id, name if name else None)
        
        # Get updated user data
        user = get_user_by_id(user_id)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'email_verified': bool(user.get('email_verified', 0)),
                'name': user.get('name')
            }
        }), 200
        
    except Exception as e:
        print(f"Update profile error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')

