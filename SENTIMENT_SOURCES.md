# Social Sentiment Data Sources

## ✅ No API Keys Required!

The app now uses **free sources** that don't require API approval:

### 1. **StockTwits** (Primary Source) 📈
- **Status**: ✅ **FREE - No API key needed!**
- **How it works**: Uses StockTwits public API
- **Data**: Real sentiment from stock traders and investors
- **Rate Limits**: Generous limits for personal use
- **Implementation**: Already working!

### 2. **Reddit** (Scraped) 💬
- **Status**: ✅ **FREE - No API key needed!**
- **How it works**: Simple web scraping of Reddit's public JSON endpoints
- **Data**: Searches r/stocks, r/investing, r/StockMarket, r/wallstreetbets
- **Note**: 
  - Reddit's ToS allows scraping for personal/educational use
  - Be respectful - don't make too many requests
  - Uses proper User-Agent header
- **Implementation**: Already working!

### 3. **Twitter/X** (Optional) 🐦
- **Status**: ⚠️ Requires API key (paid tier)
- **Current**: Uses calculated sentiment based on stock performance
- **Future**: Can add real Twitter API if you get a key
- **Note**: Twitter API v2 requires paid subscription for most use cases

## How It Works

1. **StockTwits**: 
   - Fetches recent messages about the stock
   - Analyzes keywords (bull/bear, buy/sell, etc.)
   - Calculates positive/neutral/negative percentages

2. **Reddit**:
   - Searches multiple stock-related subreddits
   - Analyzes post titles and content
   - Provides sentiment breakdown

3. **Twitter**:
   - Currently uses calculated sentiment
   - Can be upgraded with API key if needed

## Benefits

✅ **No API approval needed** - Just works!
✅ **Real data** from StockTwits and Reddit
✅ **Free** - No costs
✅ **Respectful** - Uses public APIs and proper headers

## Rate Limits

- **StockTwits**: Very generous, no issues for personal use
- **Reddit**: ~60 requests per minute (plenty for this app)
- **Twitter**: N/A (using calculated data)

## Troubleshooting

**StockTwits not working?**
- Check internet connection
- StockTwits API might be temporarily down
- Falls back to calculated sentiment automatically

**Reddit not working?**
- Reddit might be rate-limiting (wait a minute)
- Some subreddits might be private
- Falls back to calculated sentiment automatically

**Want to add Twitter API?**
- Get Twitter API v2 Bearer Token
- Add to `.env`: `TWITTER_BEARER_TOKEN=your_token`
- Code will automatically use it

