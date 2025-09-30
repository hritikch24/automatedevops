#!/usr/bin/env python3
"""
Daily US Stock Analyzer
Analyzes top US stocks and recommends top 5 picks using AI
"""

import os
import json
import requests
from datetime import datetime, timedelta
import yfinance as yf
from openai import OpenAI

# Top US stocks to analyze (can be expanded)
STOCK_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
    'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC',
    'ADBE', 'CRM', 'NFLX', 'INTC', 'AMD', 'PYPL', 'COST', 'PFE', 'KO',
    'CSCO', 'PEP', 'TMO'
]

def get_stock_data(symbol):
    """Fetch stock data and metrics"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period='3mo')

        if hist.empty:
            return None

        # Calculate metrics
        current_price = hist['Close'].iloc[-1]
        price_change_1d = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
        price_change_1w = ((current_price - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100) if len(hist) > 5 else 0
        price_change_1m = ((current_price - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20] * 100) if len(hist) > 20 else 0
        price_change_3m = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)

        avg_volume = hist['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'current_price': round(current_price, 2),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('forwardPE', info.get('trailingPE', 'N/A')),
            'price_change_1d': round(price_change_1d, 2),
            'price_change_1w': round(price_change_1w, 2),
            'price_change_1m': round(price_change_1m, 2),
            'price_change_3m': round(price_change_3m, 2),
            'volume_ratio': round(volume_ratio, 2),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'analyst_target': info.get('targetMeanPrice', 'N/A'),
            'recommendation': info.get('recommendationKey', 'N/A')
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def analyze_stocks_with_ai(stocks_data):
    """Use OpenAI to analyze stocks and pick top 5"""
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    # Prepare data for AI analysis
    stocks_summary = []
    for stock in stocks_data:
        stocks_summary.append(
            f"{stock['symbol']} ({stock['name']}) - ${stock['current_price']}\n"
            f"  Sector: {stock['sector']} | Industry: {stock['industry']}\n"
            f"  Market Cap: ${stock['market_cap']:,} | P/E: {stock['pe_ratio']}\n"
            f"  Performance: 1D: {stock['price_change_1d']}%, 1W: {stock['price_change_1w']}%, "
            f"1M: {stock['price_change_1m']}%, 3M: {stock['price_change_3m']}%\n"
            f"  Volume Ratio: {stock['volume_ratio']}x | Analyst Target: ${stock['analyst_target']}\n"
            f"  Recommendation: {stock['recommendation']}\n"
        )

    prompt = f"""You are a professional stock analyst. Today is {datetime.now().strftime('%Y-%m-%d')}.

Analyze the following {len(stocks_data)} US stocks and select the TOP 5 BEST PICKS for investment TODAY based on:
1. Technical momentum (price trends, volume)
2. Fundamental strength (P/E ratio, market cap, sector health)
3. Recent performance and volatility
4. Analyst recommendations
5. Current market conditions

STOCKS DATA:
{chr(10).join(stocks_summary)}

Provide your analysis in this EXACT JSON format:
{{
  "analysis_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "market_summary": "Brief 2-3 sentence market overview",
  "top_picks": [
    {{
      "rank": 1,
      "symbol": "SYMBOL",
      "name": "Company Name",
      "current_price": 123.45,
      "reason": "Detailed 2-3 sentence reason for this pick",
      "target_price": 150.00,
      "risk_level": "Low/Medium/High",
      "time_horizon": "Short/Medium/Long-term"
    }}
  ],
  "overall_strategy": "2-3 sentences on recommended overall strategy"
}}

Return ONLY valid JSON, no markdown or explanations."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert stock analyst providing data-driven investment recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        result = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
            result = result.strip()

        return json.loads(result)
    except Exception as e:
        print(f"Error with AI analysis: {e}")
        return None

def send_email_notification(analysis):
    """Send email with stock picks using a simple email service"""
    # Using Mailgun API (you can use SendGrid, AWS SES, etc.)
    mailgun_domain = os.environ.get('MAILGUN_DOMAIN')
    mailgun_api_key = os.environ.get('MAILGUN_API_KEY')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')

    if not all([mailgun_domain, mailgun_api_key, recipient_email]):
        print("Email credentials not configured, skipping email")
        return False

    # Format email content
    email_body = f"""
<h2>🚀 Daily Top 5 US Stock Picks - {analysis['analysis_date']}</h2>

<h3>📊 Market Summary</h3>
<p>{analysis['market_summary']}</p>

<h3>🎯 Top 5 Stock Picks</h3>
"""

    for pick in analysis['top_picks']:
        email_body += f"""
<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
    <h4>#{pick['rank']} - {pick['symbol']} ({pick['name']})</h4>
    <p><strong>Current Price:</strong> ${pick['current_price']}</p>
    <p><strong>Target Price:</strong> ${pick['target_price']}</p>
    <p><strong>Risk Level:</strong> {pick['risk_level']}</p>
    <p><strong>Time Horizon:</strong> {pick['time_horizon']}</p>
    <p><strong>Analysis:</strong> {pick['reason']}</p>
</div>
"""

    email_body += f"""
<h3>📈 Strategy Recommendation</h3>
<p>{analysis['overall_strategy']}</p>

<hr>
<p style="color: #666; font-size: 12px;">
<em>Disclaimer: This is automated analysis for informational purposes only.
Not financial advice. Always do your own research and consult with a financial advisor.</em>
</p>
"""

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"Stock Analyzer <stocks@{mailgun_domain}>",
                "to": recipient_email,
                "subject": f"📈 Top 5 US Stock Picks - {analysis['analysis_date']}",
                "html": email_body
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def create_github_issue(analysis, repo_token):
    """Create a GitHub issue with the analysis"""
    repo = os.environ.get('GITHUB_REPOSITORY')

    if not repo or not repo_token:
        print("GitHub repository info not available")
        return False

    issue_body = f"""## 📊 Daily Stock Analysis - {analysis['analysis_date']}

### Market Summary
{analysis['market_summary']}

### 🎯 Top 5 Stock Picks

"""

    for pick in analysis['top_picks']:
        issue_body += f"""
#### #{pick['rank']} - {pick['symbol']} ({pick['name']})

- **Current Price:** ${pick['current_price']}
- **Target Price:** ${pick['target_price']}
- **Risk Level:** {pick['risk_level']}
- **Time Horizon:** {pick['time_horizon']}

**Analysis:** {pick['reason']}

---

"""

    issue_body += f"""
### 📈 Overall Strategy
{analysis['overall_strategy']}

---

*Automated analysis generated using AI. Not financial advice. DYOR.*
"""

    try:
        response = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers={
                "Authorization": f"token {repo_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "title": f"📈 Top 5 Stock Picks - {analysis['analysis_date']}",
                "body": issue_body,
                "labels": ["stock-analysis", "automated"]
            }
        )
        return response.status_code == 201
    except Exception as e:
        print(f"Error creating GitHub issue: {e}")
        return False

def main():
    print(f"Starting stock analysis for {datetime.now().strftime('%Y-%m-%d')}")

    # Fetch stock data
    print(f"Fetching data for {len(STOCK_SYMBOLS)} stocks...")
    stocks_data = []
    for symbol in STOCK_SYMBOLS:
        data = get_stock_data(symbol)
        if data:
            stocks_data.append(data)
            print(f"  ✓ {symbol}: ${data['current_price']}")

    print(f"\nSuccessfully fetched data for {len(stocks_data)} stocks")

    if len(stocks_data) < 5:
        print("Not enough stock data to analyze")
        return

    # Analyze with AI
    print("\nAnalyzing stocks with AI...")
    analysis = analyze_stocks_with_ai(stocks_data)

    if not analysis:
        print("Failed to get AI analysis")
        return

    print("\n" + "="*60)
    print(f"TOP 5 STOCK PICKS - {analysis['analysis_date']}")
    print("="*60)
    print(f"\nMarket Summary: {analysis['market_summary']}\n")

    for pick in analysis['top_picks']:
        print(f"#{pick['rank']} - {pick['symbol']} ({pick['name']})")
        print(f"  Price: ${pick['current_price']} → Target: ${pick['target_price']}")
        print(f"  Risk: {pick['risk_level']} | Horizon: {pick['time_horizon']}")
        print(f"  Reason: {pick['reason']}\n")

    print(f"Strategy: {analysis['overall_strategy']}")
    print("="*60)

    # Save to file
    with open('latest_stock_picks.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    print("\n✓ Saved analysis to latest_stock_picks.json")

    # Send notifications
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        if create_github_issue(analysis, github_token):
            print("✓ Created GitHub issue with analysis")

    if send_email_notification(analysis):
        print("✓ Sent email notification")

    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
