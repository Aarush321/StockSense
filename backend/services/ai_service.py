import os
from typing import Dict, List
import anthropic
import openai

class AIService:
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        
        # Initialize clients
        self.claude_client = None
        self.openai_client = None
        
        if self.anthropic_key and 'your_' not in self.anthropic_key:
            try:
                # Initialize Anthropic client - explicitly only pass api_key
                # Clear any proxy-related environment variables that might interfere
                import os as os_env
                old_http_proxy = os_env.environ.pop('HTTP_PROXY', None)
                old_https_proxy = os_env.environ.pop('HTTPS_PROXY', None)
                try:
                    self.claude_client = anthropic.Anthropic(api_key=self.anthropic_key)
                    print(f"✅ Anthropic client initialized (key length: {len(self.anthropic_key)})")
                finally:
                    # Restore proxy env vars if they existed
                    if old_http_proxy:
                        os_env.environ['HTTP_PROXY'] = old_http_proxy
                    if old_https_proxy:
                        os_env.environ['HTTPS_PROXY'] = old_https_proxy
            except Exception as e:
                print(f"❌ Failed to initialize Anthropic client: {e}")
        
        if self.openai_key and 'your_' not in self.openai_key:
            try:
                # Initialize OpenAI client - explicitly only pass api_key
                # Clear any proxy-related environment variables that might interfere
                import os as os_env
                old_http_proxy = os_env.environ.pop('HTTP_PROXY', None)
                old_https_proxy = os_env.environ.pop('HTTPS_PROXY', None)
                try:
                    self.openai_client = openai.OpenAI(api_key=self.openai_key)
                    print(f"✅ OpenAI client initialized (key length: {len(self.openai_key)})")
                finally:
                    # Restore proxy env vars if they existed
                    if old_http_proxy:
                        os_env.environ['HTTP_PROXY'] = old_http_proxy
                    if old_https_proxy:
                        os_env.environ['HTTPS_PROXY'] = old_https_proxy
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI client: {e}")
        
        if not self.claude_client and not self.openai_client:
            print("⚠️  WARNING: No AI clients initialized. Chatbot will use fallback responses.")
    
    def generate_recommendation(self, symbol: str, company_data: Dict, news_data: Dict, 
                               sentiment_data: Dict, analyst_data: Dict) -> Dict:
        """Generate AI-powered recommendation"""
        
        # Build comprehensive context for AI
        company_desc = company_data.get('description', 'No description available.')
        
        # Format financial metrics
        pe_ratio = company_data.get('peRatio')
        pb_ratio = company_data.get('pbRatio')
        current_ratio = company_data.get('currentRatio')
        total_debt = company_data.get('totalDebt', 0)
        current_assets = company_data.get('currentAssets', 0)
        debt_to_current = company_data.get('debtToCurrentAssetsRatio')
        trailing_eps = company_data.get('trailingEps')
        earnings_growth = company_data.get('earningsGrowth')
        dividend_yield = company_data.get('dividendYield')
        has_dividend = company_data.get('hasDividend', False)
        profit_margins = company_data.get('profitMargins')
        credit_rating = company_data.get('creditRating')
        
        context = f"""
Stock Symbol: {symbol}

COMPANY OVERVIEW:
{company_desc}

BASIC INFORMATION:
- Company Name: {company_data.get('name', 'N/A')}
- Sector: {company_data.get('sector', 'N/A')}
- Industry: {company_data.get('industry', 'N/A')}
- Current Stock Price: ${company_data.get('currentPrice', 0):.2f}
- Price Change Today: {company_data.get('changePercent', 0):.2f}%
- Market Capitalization: ${company_data.get('marketCap', 0):,}
- Years Public: {company_data.get('yearsPublic', 'N/A')} years

FINANCIAL METRICS FOR VALUE INVESTING ANALYSIS:

1. VALUATION METRICS:
- P/E Ratio (Price-to-Earnings): {pe_ratio if pe_ratio else 'Not available'}
  (Lower is better. Good: under 15-20. Shows if stock is cheap relative to earnings)
- P/B Ratio (Price-to-Book): {pb_ratio if pb_ratio else 'Not available'}
  (Lower is better. Good: around 1.2 or lower. Shows if stock trades below asset value)

2. DEBT ANALYSIS:
- Total Debt: {'$' + f"{total_debt:,.0f}" if total_debt else 'Not available'}
- Current Assets: {'$' + f"{current_assets:,.0f}" if current_assets else 'Not available'}
- Debt to Current Assets Ratio: {f"{debt_to_current:.1f}%" if debt_to_current else "Not available"}
  (Good: debt under 110% of current assets indicates conservative financing)

3. LIQUIDITY:
- Current Ratio (Current Assets / Current Liabilities): {current_ratio if current_ratio else 'Not available'}
  (Good: 1.5 or higher indicates strong liquidity and ability to pay short-term obligations)

4. EARNINGS QUALITY:
- Trailing EPS (Earnings Per Share): {'$' + f"{trailing_eps:.2f}" if trailing_eps else 'Not available'}
- Earnings Growth: {f"{earnings_growth:.1f}%" if earnings_growth else 'Not available'}
  (Look for consistent positive growth)

5. DIVIDEND HISTORY:
- Pays Dividends: {'Yes' if has_dividend else 'No'}
- Dividend Yield: {f"{dividend_yield:.2f}%" if dividend_yield else 'Not available'}
  (Look for 20+ years of continuous dividend payments for financial health)

6. PROFITABILITY:
- Profit Margins: {f"{profit_margins:.2f}%" if profit_margins else 'Not available'}
  (Higher margins indicate efficient operations)

7. QUALITY RATING:
- Credit Rating: {credit_rating if credit_rating else 'Not available'}
  (Seek S&P B+ or better for quality companies)

Recent News Summary:
{self._format_news(news_data)}

Social Sentiment:
- Reddit: {sentiment_data.get('reddit', {}).get('positive', 0)}% Positive, {sentiment_data.get('reddit', {}).get('negative', 0)}% Negative
- Twitter: {sentiment_data.get('twitter', {}).get('positive', 0)}% Positive, {sentiment_data.get('twitter', {}).get('negative', 0)}% Negative

Professional Analyst Opinions:
- Buy Recommendations: {analyst_data.get('buyCount', 0)}
- Hold Recommendations: {analyst_data.get('holdCount', 0)}
- Sell Recommendations: {analyst_data.get('sellCount', 0)}
- Average Price Target: ${analyst_data.get('averagePriceTarget', 'N/A')}
"""
        
        prompt = f"""{context}

Based on the comprehensive information above, provide a balanced, educational investment analysis for {symbol}. 

CRITICAL INSTRUCTIONS:
- DO NOT provide direct buy/hold/sell recommendations
- Present facts objectively and let the user draw their own conclusions
- Focus on EDUCATION: explain what metrics mean and their implications
- Be balanced - every company has both strengths and weaknesses
- Use simple, clear language suitable for beginners

REQUIRED ANALYSIS STRUCTURE (follow exactly):

1. **Company Description** (exactly 3 sentences):
   - Sentence 1: Core business and main products/services
   - Sentence 2: Target market or customer base
   - Sentence 3: Market position or competitive advantage

2. **Recent News Summary** (exactly 2 sentences):
   - Sentence 1: Summarize what the stock has been doing recently - major changes, developments, or significant events affecting the company
   - Sentence 2: Describe any additional recent developments, market reactions, or notable changes in the stock's performance or business

3. **Reasons to Buy for Long-Term** (up to 5 bullet points):
   Each bullet point must have:
   - **Bold title** followed by 1-2 sentence explanation
   - Focus on fundamentals: revenue growth, profitability, competitive advantages, market trends, innovation, etc.
   - Example format: **Strong Financial Position**: The company maintains healthy profit margins and consistent earnings growth...

4. **Reasons Not to Buy for Long-Term** (up to 5 bullet points):
   Each bullet point must have:
   - **Bold title** followed by 1-2 sentence explanation
   - Focus on risks: valuation concerns, competition, regulatory issues, debt levels, market saturation, etc.
   - Example format: **High Valuation**: The current P/E ratio suggests the stock may be priced above intrinsic value...

5. **Long-Term Risk Assessment** (2-3 sentences):
   - Evaluate overall risk level (Low/Medium/High) with explanation
   - Mention specific risk factors that could impact long-term holding

6. **Market Correlation** (exactly 2 sentences):
   - Sentence 1: Does this stock follow the broader market (S&P 500) closely or move independently?
   - Sentence 2: Explain what this means for diversification

7. **Short-Term Tendencies** (2-3 sentences):
   - Describe the stock's volatility and short-term price behavior
   - Mention if it's prone to sharp swings, steady, or reactive to news

8. **Summary** (3-4 sentences):
   - Synthesize the key points WITHOUT giving a direct buy/hold/sell recommendation
   - Present the investment case objectively
   - Let the user draw their own conclusion from the facts presented

WRITING STYLE:
- Use clear, professional language
- Explain financial terms when first used
- Be objective and factual
- Present both positive and negative aspects fairly
- Do NOT end with "you should buy/sell/hold" - let the facts speak for themselves
"""
        
        # Try Claude first (faster), then OpenAI, then return mock
        # Use shorter timeout by trying faster models first
        try:
            if self.claude_client:
                return self._get_claude_recommendation(prompt)
        except Exception as e:
            print(f"Claude recommendation error: {e}")
        
        try:
            if self.openai_client:
                return self._get_openai_recommendation(prompt)
        except Exception as e:
            print(f"OpenAI recommendation error: {e}")
        
        # Fallback to mock recommendation if no API keys or all failed
        return self._get_mock_recommendation(symbol, company_data, analyst_data, news_data)
    
    def _get_claude_recommendation(self, prompt: str) -> Dict:
        """Get recommendation from Claude API - optimized for speed"""
        # Try faster model first (haiku), fallback to sonnet if needed
        models_to_try = [
            ("claude-3-haiku-20240307", 1200),  # Fastest model, fewer tokens
            ("claude-3-5-sonnet-20241022", 1500)  # Fallback if haiku fails
        ]
        
        for model, max_tokens in models_to_try:
            try:
                message = self.claude_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                
                response_text = message.content[0].text
                
                # Extract risk level from Long-Term Risk Assessment section
                risk_level = "Medium"
                if "**Long-Term Risk Assessment**" in response_text or "5." in response_text:
                    # Try to extract risk level
                    risk_text = response_text.upper()
                    if "LOW RISK" in risk_text or ("RISK" in risk_text and "LOW" in risk_text.split("RISK")[0][-20:]):
                        risk_level = "Low"
                    elif "HIGH RISK" in risk_text or ("RISK" in risk_text and "HIGH" in risk_text.split("RISK")[0][-20:]):
                        risk_level = "High"
                
                return {
                    'recommendation': None,  # No direct recommendation
                    'reasoning': response_text,
                    'riskLevel': risk_level
                }
            except Exception as e:
                if model == models_to_try[-1][0]:  # Last model, re-raise
                    raise
                continue  # Try next model
        
        # If all models failed, raise
        raise Exception("All Claude models failed")
    
    def _get_openai_recommendation(self, prompt: str) -> Dict:
        """Get recommendation from OpenAI API"""
        # Try faster models first
        models_to_try = ["gpt-4o-mini", "gpt-4o", "gpt-4"]
        response_text = None
        for model in models_to_try:
            try:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful financial advisor who explains investment decisions in simple, beginner-friendly terms. You ALWAYS provide BALANCED analysis showing both strengths and weaknesses. No stock is perfect - you must explain what metrics mean in context, not just whether they're 'good' or 'bad'. Focus on education and helping beginners understand trade-offs."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1200,  # Reduced for faster response
                    temperature=0.7  # Slightly lower for faster generation
                )
                response_text = response.choices[0].message.content
                break  # Success
            except Exception as e:
                if model == models_to_try[-1]:  # Last model, re-raise
                    raise
                continue  # Try next model
        
        if response_text is None:
            raise Exception("All OpenAI models failed")
        
        # Extract risk level from Long-Term Risk Assessment section
        risk_level = "Medium"
        risk_text = response_text.upper()
        if "LOW RISK" in risk_text or ("RISK" in risk_text and "LOW" in risk_text.split("RISK")[0][-20:]):
            risk_level = "Low"
        elif "HIGH RISK" in risk_text or ("RISK" in risk_text and "HIGH" in risk_text.split("RISK")[0][-20:]):
            risk_level = "High"
        
        return {
            'recommendation': None,  # No direct recommendation
            'reasoning': response_text,
            'riskLevel': risk_level
        }
    
    def _get_mock_recommendation(self, symbol: str, company_data: Dict, analyst_data: Dict, news_data: list = None) -> Dict:
        """Generate a balanced mock recommendation following the new structure"""
        buy_count = analyst_data.get('buyCount', 0)
        sell_count = analyst_data.get('sellCount', 0)
        
        # Get financial metrics
        pe_ratio = company_data.get('peRatio')
        pb_ratio = company_data.get('pbRatio')
        current_ratio = company_data.get('currentRatio')
        debt_to_current = company_data.get('debtToCurrentAssetsRatio')
        earnings_growth = company_data.get('earningsGrowth')
        has_dividend = company_data.get('hasDividend', False)
        profit_margins = company_data.get('profitMargins')
        dividend_yield = company_data.get('dividendYield')
        trailing_eps = company_data.get('trailingEps')
        sector = company_data.get('sector', 'N/A')
        industry = company_data.get('industry', 'N/A')
        
        company_name = company_data.get('name', symbol)
        description = company_data.get('description', '') or 'No detailed description available.'
        
        # Parse description into sentences for company description
        desc_sentences = [s.strip() for s in description.split('.') if s.strip()][:3]
        if len(desc_sentences) < 3:
            # Create 3 sentences from available info
            sentence1 = f"{company_name} operates in the {industry} sector"
            sentence2 = f"The company serves customers in the {sector} market"
            sentence3 = f"{company_name} competes in the {industry} industry"
            if desc_sentences:
                sentence1 = desc_sentences[0] if len(desc_sentences) > 0 else sentence1
                sentence2 = desc_sentences[1] if len(desc_sentences) > 1 else sentence2
                sentence3 = desc_sentences[2] if len(desc_sentences) > 2 else sentence3
        else:
            sentence1, sentence2, sentence3 = desc_sentences[0], desc_sentences[1], desc_sentences[2]
        
        reasoning_parts = []
        buy_reasons = []
        not_buy_reasons = []
        
        # 1. Company Description (3 sentences)
        company_desc = f"**1. Company Description**\n\n{sentence1}. {sentence2}. {sentence3}."
        reasoning_parts.append(company_desc)
        
        # 2. Recent News Summary (2 sentences) - Focus on what the stock has been doing recently
        news_summary = "**2. Recent News Summary**\n\n"
        if news_data and len(news_data) > 0:
            # Synthesize news into what the stock/company has been doing
            headlines = [article.get('headline', '') for article in news_data[:3]]
            # Create a summary of recent developments
            first_sentence = f"Recently, {symbol} has been "
            if any('earnings' in h.lower() or 'revenue' in h.lower() or 'profit' in h.lower() for h in headlines):
                first_sentence += "experiencing developments related to its financial performance and business operations."
            elif any('acquisition' in h.lower() or 'merger' in h.lower() or 'deal' in h.lower() for h in headlines):
                first_sentence += "involved in strategic business moves including potential acquisitions or partnerships."
            elif any('launch' in h.lower() or 'product' in h.lower() or 'innovation' in h.lower() for h in headlines):
                first_sentence += "focusing on product launches and innovation initiatives."
            elif any('regulation' in h.lower() or 'legal' in h.lower() or 'lawsuit' in h.lower() for h in headlines):
                first_sentence += "facing regulatory or legal developments that may impact its operations."
            else:
                first_sentence += "experiencing market activity and developments that reflect ongoing business operations."
            
            second_sentence = "The stock has shown "
            change_percent = company_data.get('changePercent', 0)
            if abs(change_percent) > 5:
                if change_percent > 0:
                    second_sentence += f"significant positive movement with a {change_percent:.1f}% change, indicating strong investor interest."
                else:
                    second_sentence += f"notable downward pressure with a {change_percent:.1f}% decline, reflecting market concerns."
            else:
                second_sentence += "relatively stable price movement, suggesting steady investor sentiment."
            
            news_summary += first_sentence + " " + second_sentence
        else:
            change_percent = company_data.get('changePercent', 0)
            news_summary += f"Recently, {symbol} has been experiencing normal market activity with limited major developments reported. "
            if abs(change_percent) > 2:
                news_summary += f"The stock has shown a {change_percent:.1f}% price movement, indicating some market activity."
            else:
                news_summary += "The stock has maintained relatively stable trading patterns."
        reasoning_parts.append(news_summary)
        
        # 3. Reasons to Buy for Long-Term (up to 5 bullet points with bold titles)
        buy_reasons_text = "\n**3. Reasons to Buy for Long-Term**\n\n"
        
        if pe_ratio and pe_ratio < 20:
            buy_reasons.append(("**Reasonable Valuation**", f"The P/E ratio of {pe_ratio:.1f} suggests the stock may be reasonably priced relative to earnings, providing potential value for long-term investors."))
        
        if pb_ratio and pb_ratio <= 1.5:
            buy_reasons.append(("**Attractive Price-to-Book Ratio**", f"With a P/B ratio of {pb_ratio:.2f}, the stock trades near or below its asset value, which can be attractive for value-oriented investors."))
        
        if current_ratio and current_ratio >= 1.5:
            buy_reasons.append(("**Strong Financial Health**", f"The current ratio of {current_ratio:.2f} indicates strong liquidity and the company's ability to meet short-term obligations, suggesting financial stability."))
        
        if earnings_growth is not None and earnings_growth > 0:
            buy_reasons.append(("**Positive Earnings Growth**", f"Earnings growth of {earnings_growth:.1f}% demonstrates the company's ability to expand profitability, which is fundamental for long-term value creation."))
        
        if profit_margins is not None and profit_margins > 10:
            buy_reasons.append(("**Healthy Profit Margins**", f"Profit margins of {profit_margins:.2f}% indicate efficient operations and potential pricing power, suggesting a strong business model."))
        
        if has_dividend:
            buy_reasons.append(("**Dividend Income**", f"The company pays dividends, providing income to shareholders and typically indicating financial stability and commitment to shareholder returns."))
        
        if buy_count > sell_count:
            buy_reasons.append(("**Positive Analyst Sentiment**", f"Professional analysts show more buy than sell recommendations, suggesting institutional confidence in the company's prospects."))
        
        if debt_to_current and debt_to_current <= 110:
            buy_reasons.append(("**Conservative Debt Management**", f"Debt levels are conservative relative to current assets, indicating prudent financial management and lower financial risk."))
        
        # Limit to 5 reasons
        for i, (title, explanation) in enumerate(buy_reasons[:5], 1):
            buy_reasons_text += f"• {title}: {explanation}\n\n"
        
        if not buy_reasons:
            buy_reasons_text += "• **Stable Operations**: The company maintains consistent business operations in its sector.\n\n"
        
        reasoning_parts.append(buy_reasons_text)
        
        # 4. Reasons Not to Buy for Long-Term (up to 5 bullet points with bold titles)
        not_buy_reasons_text = "\n**4. Reasons Not to Buy for Long-Term**\n\n"
        
        if pe_ratio and pe_ratio > 25:
            not_buy_reasons.append(("**High Valuation**", f"The P/E ratio of {pe_ratio:.1f} suggests the stock may be overvalued, requiring strong future growth to justify the premium price."))
        
        if pb_ratio and pb_ratio > 2.0:
            not_buy_reasons.append(("**Premium Pricing**", f"With a P/B ratio of {pb_ratio:.2f}, the stock trades significantly above its book value, which may limit upside potential."))
        
        if current_ratio and current_ratio < 1.0:
            not_buy_reasons.append(("**Liquidity Concerns**", f"The current ratio of {current_ratio:.2f} is below 1.0, which may indicate challenges in meeting short-term obligations and financial stress."))
        
        if earnings_growth is not None and earnings_growth < 0:
            not_buy_reasons.append(("**Declining Earnings**", f"Negative earnings growth of {earnings_growth:.1f}% raises concerns about the company's ability to maintain profitability and create shareholder value."))
        
        if profit_margins is not None and profit_margins < 5:
            not_buy_reasons.append(("**Thin Profit Margins**", f"Low profit margins of {profit_margins:.2f}% may indicate pricing pressure, high costs, or competitive challenges that could impact long-term sustainability."))
        
        if debt_to_current and debt_to_current > 150:
            not_buy_reasons.append(("**High Debt Levels**", f"Debt significantly exceeds current assets, which increases financial risk and may limit the company's flexibility during economic downturns."))
        
        if sell_count > buy_count:
            not_buy_reasons.append(("**Cautious Analyst Outlook**", f"More analysts recommend selling than buying, suggesting professional concerns about the company's near-term prospects."))
        
        if not has_dividend:
            not_buy_reasons.append(("**No Dividend Income**", f"The company does not pay dividends, which means investors rely solely on capital appreciation and miss out on regular income streams."))
        
        # Limit to 5 reasons
        for i, (title, explanation) in enumerate(not_buy_reasons[:5], 1):
            not_buy_reasons_text += f"• {title}: {explanation}\n\n"
        
        if not not_buy_reasons:
            not_buy_reasons_text += "• **Market Risks**: All investments carry inherent market risks that could impact long-term returns.\n\n"
        
        reasoning_parts.append(not_buy_reasons_text)
        
        # 5. Long-Term Risk Assessment (2-3 sentences)
        risk_count = len(not_buy_reasons)
        strength_count = len(buy_reasons)
        
        if risk_count > strength_count * 1.5:
            risk_level = "High"
            risk_text = f"**5. Long-Term Risk Assessment**\n\nThe overall risk level for this investment is High. The company faces significant challenges including {', '.join([r[0].replace('**', '').replace('*', '') for r in not_buy_reasons[:2]])} that could impact long-term holding. Investors should carefully consider their risk tolerance and conduct thorough due diligence before committing capital."
        elif risk_count > strength_count:
            risk_level = "Medium-High"
            risk_text = f"**5. Long-Term Risk Assessment**\n\nThe overall risk level for this investment is Medium-High. While the company has some positive attributes, there are notable concerns that warrant careful monitoring. Specific risk factors include potential volatility in earnings and market conditions that could affect long-term performance."
        elif strength_count > risk_count * 1.5:
            risk_level = "Low-Medium"
            risk_text = f"**5. Long-Term Risk Assessment**\n\nThe overall risk level for this investment is Low-Medium. The company demonstrates several fundamental strengths that suggest relative stability. However, investors should remain aware of market risks and industry-specific challenges that could emerge over time."
        else:
            risk_level = "Medium"
            risk_text = f"**5. Long-Term Risk Assessment**\n\nThe overall risk level for this investment is Medium. The company presents a balanced mix of strengths and concerns typical of most publicly traded companies. Long-term investors should monitor key financial metrics and industry trends that could impact the investment over time."
        
        reasoning_parts.append(risk_text)
        
        # 6. Market Correlation (2 sentences)
        correlation_text = f"**6. Market Correlation**\n\n{symbol} generally follows the broader market trends of the S&P 500, though sector-specific factors may cause some divergence. This correlation means the stock will likely move with overall market sentiment, which provides some diversification benefit but also means it may decline during broader market downturns."
        reasoning_parts.append(correlation_text)
        
        # 7. Short-Term Tendencies (2-3 sentences)
        volatility_text = f"**7. Short-Term Tendencies**\n\n{symbol} exhibits moderate volatility typical of stocks in the {industry} sector. The stock price tends to react to earnings announcements, sector news, and broader market movements. Short-term price swings are common, making this stock more suitable for investors with a longer time horizon who can weather temporary fluctuations."
        reasoning_parts.append(volatility_text)
        
        # 8. Summary (3-4 sentences) - NO direct recommendation
        summary_text = f"**8. Summary**\n\n{company_name} operates in the {industry} sector with a mix of fundamental strengths and areas of concern. The company's financial metrics suggest {risk_level.lower()} risk characteristics, with {len(buy_reasons)} notable positive factors and {len(not_buy_reasons)} areas requiring attention. Investors should carefully weigh the company's competitive position, financial health, and growth prospects against their individual investment goals and risk tolerance. The decision to invest should be based on thorough research and alignment with one's long-term investment strategy."
        reasoning_parts.append(summary_text)
        
        full_reasoning = "\n\n".join(reasoning_parts)
        
        return {
            'recommendation': None,  # No direct recommendation
            'reasoning': full_reasoning,
            'riskLevel': risk_level,
            'note': 'This is an educational analysis based on fundamental metrics. For AI-powered analysis with deeper insights, add ANTHROPIC_API_KEY or OPENAI_API_KEY to your .env file.'
        }
    
    def _format_news(self, news_data: list) -> str:
        """Format news data for AI context"""
        if not news_data:
            return "No recent news available."
        
        formatted = []
        for i, article in enumerate(news_data[:5], 1):
            headline = article.get('headline', 'N/A')
            source = article.get('source', 'N/A')
            formatted.append(f"{i}. {headline} ({source})")
        
        return "\n".join(formatted)
    
    def chat(self, message: str, market_news: List[Dict] = None) -> str:
        """Generate chatbot response for financial education"""
        
        # Format market news if available
        news_context = ""
        if market_news:
            news_context = "\n\nRECENT MARKET NEWS (Past 24 Hours):\n"
            for i, article in enumerate(market_news[:5], 1):
                headline = article.get('headline', 'N/A')
                summary = article.get('summary', '')[:150] if article.get('summary') else ''
                news_context += f"{i}. {headline}\n   {summary}\n\n"
        
        system_prompt = """You are a financial education expert chatbot for StockSense, a beginner-friendly stock analysis tool. Your role is to help users understand financial concepts, terms, and information.

CRITICAL RULES:
1. NEVER provide buy/sell/hold recommendations for any stock, ETF, or investment
2. NEVER tell users whether they should invest in something
3. Focus on EDUCATION: explain concepts, terms, and how things work
4. Break down complex financial systems and terms into simple, beginner-friendly language
5. Use analogies and examples to make concepts clear
6. If asked about tool errors, bugs, or technical issues, politely direct users to contact the owner at aarushravi.09@gmail.com
7. If asked about specific stock recommendations or whether to buy something, explain that you're an educational tool and cannot provide investment advice
8. You have access to recent market news to provide context, but use it only for educational purposes

Your responses should be:
- Clear and easy to understand
- Educational and informative
- Beginner-friendly
- Objective and balanced
- Helpful for learning about finance and investing

Always maintain a helpful, professional, and educational tone."""

        user_prompt = f"""User Question: {message}
{news_context}

Please provide a helpful, educational response. Remember: NO buy/sell recommendations, only education and explanations."""

        # Try Claude first, then OpenAI, then fallback
        if self.claude_client:
            try:
                import sys
                sys.stderr.write("🤖 Attempting Claude API call...\n")
                sys.stderr.flush()
                # Try multiple Claude model names in order of preference
                claude_models = [
                    "claude-3-haiku-20240307",     # Fastest and most reliable
                    "claude-3-5-sonnet-20241022",  # Newer model if available
                    "claude-3-5-haiku-20241022"    # Newer haiku version
                ]
                
                for model in claude_models:
                    try:
                        sys.stderr.write(f"Trying Claude model: {model}\n")
                        sys.stderr.flush()
                        response = self.claude_client.messages.create(
                            model=model,
                            max_tokens=1000,
                            system=system_prompt,
                            messages=[{
                                "role": "user",
                                "content": user_prompt
                            }]
                        )
                        sys.stderr.write(f"✅ Claude API call successful with model: {model}\n")
                        sys.stderr.flush()
                        return response.content[0].text
                    except Exception as model_error:
                        sys.stderr.write(f"⚠️  Model {model} failed: {str(model_error)[:200]}, trying next...\n")
                        sys.stderr.flush()
                        continue
                        
            except Exception as e:
                import traceback
                sys.stderr.write(f"❌ Claude chat error: {e}\n")
                sys.stderr.write(traceback.format_exc())
                sys.stderr.flush()
        
        if self.openai_client:
            try:
                import sys
                sys.stderr.write("🤖 Attempting OpenAI API call...\n")
                sys.stderr.flush()
                # Try multiple OpenAI model names in order of preference
                # Note: If you get quota errors, check your OpenAI billing
                openai_models = [
                    "gpt-4o",              # Latest and most capable
                    "gpt-4o-mini",         # Faster and cheaper
                    "gpt-4-turbo",         # Alternative
                    "gpt-3.5-turbo"        # Fallback (most likely to work with free tier)
                ]
                
                for model in openai_models:
                    try:
                        sys.stderr.write(f"Trying OpenAI model: {model}\n")
                        sys.stderr.flush()
                        response = self.openai_client.chat.completions.create(
                            model=model,
                            max_tokens=1000,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ]
                        )
                        sys.stderr.write(f"✅ OpenAI API call successful with model: {model}\n")
                        sys.stderr.flush()
                        return response.choices[0].message.content
                    except Exception as model_error:
                        sys.stderr.write(f"⚠️  Model {model} failed: {str(model_error)[:200]}, trying next...\n")
                        sys.stderr.flush()
                        continue
                        
            except Exception as e:
                import traceback
                sys.stderr.write(f"❌ OpenAI chat error: {e}\n")
                sys.stderr.write(traceback.format_exc())
                sys.stderr.flush()
        
        # Fallback: Provide basic educational responses for common questions
        print("⚠️  Using fallback response (no AI clients available or all API calls failed)")
        return self._get_fallback_response(message.lower())
    
    def _get_fallback_response(self, message_lower: str) -> str:
        """Provide basic educational responses when AI APIs are unavailable"""
        
        # Common financial terms and concepts
        if any(term in message_lower for term in ['pe ratio', 'p/e ratio', 'price-to-earnings', 'price to earnings']):
            return """**P/E Ratio (Price-to-Earnings Ratio)**

The P/E ratio is one of the most commonly used metrics to evaluate whether a stock is overvalued or undervalued.

**What it means:**
- It compares a company's stock price to its earnings per share (EPS)
- Formula: Stock Price ÷ Earnings Per Share = P/E Ratio
- Example: If a stock costs $50 and the company earns $5 per share, the P/E ratio is 10

**How to interpret it:**
- **Lower P/E (under 15-20)**: Generally considered "cheap" - you're paying less for each dollar of earnings
- **Higher P/E (over 20-25)**: Generally considered "expensive" - you're paying more for each dollar of earnings
- **Industry comparison**: P/E ratios vary by industry, so compare a stock's P/E to others in the same sector

**Important notes:**
- A low P/E doesn't always mean a good investment - the company might have problems
- A high P/E doesn't always mean a bad investment - the company might be growing rapidly
- Always consider P/E along with other financial metrics and the company's growth prospects

Think of it like this: If you're buying a business, the P/E ratio tells you how many years of current earnings it would take to "pay back" your investment."""

        elif any(term in message_lower for term in ['dividend', 'dividends']):
            return """**Dividends**

Dividends are regular payments that some companies make to their shareholders from their profits.

**What they are:**
- Cash payments distributed to shareholders, usually quarterly (every 3 months)
- Not all companies pay dividends - growth companies often reinvest profits instead
- Expressed as a dollar amount per share or as a percentage (dividend yield)

**Example:**
- If a company pays $1 per share quarterly and you own 100 shares, you receive $100 every 3 months
- If the stock price is $50, the dividend yield is 2% ($1 ÷ $50 × 4 quarters)

**Why companies pay dividends:**
- Attract income-seeking investors
- Signal financial strength and stability
- Return excess cash to shareholders

**Important considerations:**
- Dividend yield: Annual dividend ÷ Stock price
- Dividend history: Companies with 20+ years of continuous dividends are often more stable
- Dividend sustainability: Can the company afford to keep paying?

**Note:** Dividend payments are not guaranteed and can be reduced or eliminated if the company faces financial difficulties."""

        elif any(term in message_lower for term in ['market cap', 'market capitalization', 'market cap']):
            return """**Market Capitalization (Market Cap)**

Market cap is the total value of all a company's outstanding shares of stock.

**How it's calculated:**
- Market Cap = Current Stock Price × Total Number of Shares Outstanding
- Example: If a stock costs $100 and there are 1 million shares, the market cap is $100 million

**Company size categories:**
- **Large Cap**: $10+ billion (e.g., Apple, Microsoft, Amazon)
- **Mid Cap**: $2-10 billion
- **Small Cap**: $300 million - $2 billion
- **Micro Cap**: Under $300 million

**Why it matters:**
- Indicates company size and scale
- Larger companies are generally more stable but may grow slower
- Smaller companies may have more growth potential but higher risk
- Helps compare companies of different sizes

**Important:** Market cap changes constantly as the stock price moves. It represents what investors collectively think the company is worth, not necessarily its book value or assets."""

        elif any(term in message_lower for term in ['pb ratio', 'p/b ratio', 'price-to-book', 'price to book']):
            return """**P/B Ratio (Price-to-Book Ratio)**

The P/B ratio compares a company's stock price to its book value (net assets).

**What it means:**
- Formula: Stock Price ÷ Book Value Per Share = P/B Ratio
- Book value = Total Assets - Total Liabilities (what the company is "worth" on paper)
- Example: If a stock costs $12 and book value is $10 per share, P/B = 1.2

**How to interpret it:**
- **P/B < 1.0**: Stock trades below book value (potentially undervalued)
- **P/B = 1.0-1.5**: Stock trades close to book value (fair value range)
- **P/B > 1.5**: Stock trades above book value (may be overvalued, or company has valuable intangibles)

**When it's useful:**
- Best for asset-heavy companies (banks, real estate, manufacturing)
- Less useful for tech companies with valuable intangibles (brands, patents, software)

**Think of it like:** If you're buying a house, the P/B ratio compares the selling price to what the house is worth on paper (after debts)."""

        elif any(term in message_lower for term in ['current ratio', 'liquidity']):
            return """**Current Ratio (Liquidity Ratio)**

The current ratio measures a company's ability to pay its short-term debts with its short-term assets.

**What it means:**
- Formula: Current Assets ÷ Current Liabilities = Current Ratio
- Current assets: Cash, inventory, accounts receivable (due within 1 year)
- Current liabilities: Bills, loans, accounts payable (due within 1 year)

**How to interpret it:**
- **Above 1.5**: Generally healthy - company can cover short-term obligations
- **Below 1.0**: Potential liquidity problems - may struggle to pay bills
- **Exactly 1.0**: Assets exactly match liabilities (risky)

**Example:**
- If a company has $1.5 million in current assets and $1 million in current liabilities, current ratio = 1.5
- This means the company has $1.50 available for every $1.00 it owes in the short term

**Why it matters:**
- Indicates financial health and stability
- Companies with low current ratios may face cash flow problems
- Important for assessing bankruptcy risk

**Note:** Too high a current ratio (above 3-4) might indicate the company isn't efficiently using its assets."""

        elif any(term in message_lower for term in ['eps', 'earnings per share', 'earnings']):
            return """**EPS (Earnings Per Share)**

EPS tells you how much profit a company makes for each share of stock.

**What it means:**
- Formula: (Net Income - Preferred Dividends) ÷ Number of Outstanding Shares = EPS
- Shows profitability on a per-share basis
- Example: If a company earns $10 million and has 5 million shares, EPS = $2.00

**Types of EPS:**
- **Trailing EPS**: Based on past 12 months of earnings (most common)
- **Forward EPS**: Estimated future earnings (projections)

**How to use it:**
- Compare EPS across companies in the same industry
- Track EPS growth over time (increasing is generally good)
- Used to calculate P/E ratio (Price ÷ EPS = P/E)

**Important considerations:**
- Higher EPS is generally better, but context matters
- Compare to previous periods to see growth trends
- One-time events can skew EPS (look for consistent patterns)

**Think of it like:** If you own a pizza shop with 4 partners, EPS tells you how much profit each partner gets per "share" of ownership."""

        elif any(term in message_lower for term in ['debt', 'leverage', 'liabilities']):
            return """**Debt and Leverage**

Debt is money a company borrows that must be repaid, usually with interest.

**Types of debt:**
- **Short-term debt**: Due within 1 year (bills, short loans)
- **Long-term debt**: Due after 1 year (bonds, mortgages, long-term loans)
- **Total debt**: Sum of all borrowing

**Why companies use debt:**
- Finance growth and expansion
- Take advantage of opportunities
- Benefit from tax deductions on interest payments

**How to evaluate debt:**
- **Debt-to-equity ratio**: Total debt ÷ Shareholders' equity (lower is generally better)
- **Debt-to-assets ratio**: Total debt ÷ Total assets
- **Interest coverage**: Can the company afford interest payments?

**Conservative approach:**
- Total debt should be under 110% of current assets
- Company should generate enough cash flow to service debt
- Low debt = less risk but potentially slower growth

**High debt risks:**
- Interest payments reduce profits
- Economic downturns can make repayment difficult
- May limit future borrowing capacity

**Remember:** Some debt is normal and healthy, but excessive debt increases bankruptcy risk."""

        elif any(term in message_lower for term in ['stock market', 'how does the stock market work', 'what is the stock market']):
            return """**How the Stock Market Works**

The stock market is a place where people buy and sell shares of publicly traded companies.

**Basic concepts:**
- **Stock/Share**: A small piece of ownership in a company
- **Stock Exchange**: Where stocks are traded (NYSE, NASDAQ)
- **Stock Price**: Determined by supply and demand - what buyers are willing to pay

**How it works:**
1. Companies "go public" (IPO) and sell shares to raise money
2. Investors buy shares, becoming partial owners
3. Share prices fluctuate based on:
   - Company performance (earnings, growth)
   - Economic conditions
   - Investor sentiment
   - News and events

**Why prices change:**
- **Supply and demand**: More buyers = higher price, more sellers = lower price
- **Company news**: Good earnings = price up, bad news = price down
- **Market sentiment**: Overall optimism or pessimism
- **Economic factors**: Interest rates, inflation, unemployment

**Key players:**
- **Investors**: Buy and hold stocks for long-term growth
- **Traders**: Buy and sell frequently to profit from price movements
- **Companies**: Raise capital by selling shares

**Remember:** The stock market can be volatile - prices go up and down. Long-term investing typically performs better than trying to time the market."""

        # Default fallback
        api_key_status = ""
        if not self.anthropic_key and not self.openai_key:
            api_key_status = "\n\n**Note:** AI API keys are not configured. For full AI-powered responses, please add ANTHROPIC_API_KEY or OPENAI_API_KEY to your backend .env file. For technical setup issues, contact aarushravi.09@gmail.com."
        
        return f"""I'm here to help you learn about financial terms and concepts! I can explain things like:
- Financial terminology (P/E ratio, dividends, market cap, etc.)
- How different financial systems work
- Investment concepts and strategies (for educational purposes)
- Market trends and news (for context only)

However, I cannot provide buy/sell recommendations. For technical issues with the tool, please contact aarushravi.09@gmail.com.

**Common topics I can explain:**
- P/E Ratio (Price-to-Earnings)
- Dividends
- Market Capitalization
- P/B Ratio (Price-to-Book)
- Current Ratio and Liquidity
- EPS (Earnings Per Share)
- Debt and Leverage
- How the Stock Market Works

What specific financial term or concept would you like to learn about?{api_key_status}"""

