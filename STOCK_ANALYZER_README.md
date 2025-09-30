# 📈 Daily US Stock Analyzer with AI

Automated GitHub Action that analyzes top US stocks daily and recommends the **Top 5 Best Picks** using AI (OpenAI GPT-4).

## 🚀 Features

- **Automated Daily Analysis** - Runs every weekday at 9:30 AM EST (after US market opens)
- **AI-Powered Recommendations** - Uses OpenAI GPT-4 to analyze 30+ top US stocks
- **Multiple Notification Methods**:
  - GitHub Issues (automatic)
  - Email notifications (optional)
  - JSON file commit to repository
- **Comprehensive Analysis** including:
  - Technical momentum (price trends, volume)
  - Fundamental metrics (P/E ratio, market cap)
  - Sector health and analyst recommendations
  - Risk level and time horizon for each pick

## 📊 Analyzed Stocks

The system analyzes 30 major US stocks including:
- **Tech**: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, AMD, INTC, ADBE, CRM, NFLX
- **Finance**: JPM, BAC, V, MA
- **Healthcare**: JNJ, UNH, PFE, TMO
- **Consumer**: WMT, PG, HD, DIS, COST, KO, PEP
- **Payments**: PYPL
- **Networking**: CSCO
- **Holding**: BRK-B

## 🛠️ Setup Instructions

### 1. Enable GitHub Actions

Ensure GitHub Actions is enabled in your repository:
- Go to **Settings** → **Actions** → **General**
- Select **Allow all actions and reusable workflows**

### 2. Configure Secrets

Go to **Settings** → **Secrets and variables** → **Actions** and add:

#### Required Secrets:

**`OPENAI_API_KEY`** (Required)
- Get from: https://platform.openai.com/api-keys
- This is used for AI-powered stock analysis
- Cost: ~$0.05-0.10 per analysis (GPT-4o)

#### Optional Secrets (for Email Notifications):

**`MAILGUN_API_KEY`**
- Get from: https://www.mailgun.com/ (Free tier: 5,000 emails/month)
- Create account and get API key from Dashboard

**`MAILGUN_DOMAIN`**
- Your Mailgun sending domain (e.g., `mg.yourdomain.com`)
- Set up in Mailgun dashboard

**`RECIPIENT_EMAIL`**
- Email address to receive daily stock picks

> **Note:** If email secrets are not configured, the action will still work and create GitHub issues.

### 3. Enable Issue Creation

The workflow needs permission to create issues:
- Go to **Settings** → **Actions** → **General**
- Scroll to **Workflow permissions**
- Select **Read and write permissions**
- Check **Allow GitHub Actions to create and approve pull requests**
- Click **Save**

### 4. Trigger the Workflow

#### Automatic (Daily):
- Runs Monday-Friday at **9:30 AM EST** (2:30 PM UTC)
- No action needed - just wait for it to run

#### Manual Trigger:
1. Go to **Actions** tab
2. Click **Daily US Stock Analysis**
3. Click **Run workflow** → **Run workflow**

## 📧 Email Setup (Optional)

### Using Mailgun (Recommended - Free Tier Available):

1. Sign up at https://www.mailgun.com/
2. Verify your domain or use Mailgun's sandbox domain
3. Get your API key from **Settings** → **API Keys**
4. Add the following secrets to GitHub:
   - `MAILGUN_API_KEY`
   - `MAILGUN_DOMAIN` (e.g., `sandbox123.mailgun.org`)
   - `RECIPIENT_EMAIL` (your email)

### Alternative Email Services:

You can modify the `stock_analyzer.py` script to use:
- **SendGrid** (12,000 emails/month free)
- **AWS SES** (62,000 emails/month free)
- **Gmail SMTP** (basic, not recommended for automation)

## 📋 Output Format

The analysis provides:

### Market Summary
Brief overview of current market conditions

### Top 5 Stock Picks
For each pick:
- **Rank** (#1-5)
- **Symbol & Company Name**
- **Current Price**
- **Target Price**
- **Risk Level** (Low/Medium/High)
- **Time Horizon** (Short/Medium/Long-term)
- **Detailed Analysis** (2-3 sentences explaining the pick)

### Overall Strategy
Recommended investment strategy based on market conditions

## 📁 Files Created

- **`latest_stock_picks.json`** - Most recent analysis (committed to repo)
- **GitHub Issue** - Created for each analysis with full details
- **Email** - Sent to configured recipient (if enabled)
- **Artifacts** - 30-day retention in GitHub Actions

## 🔧 Customization

### Change Analysis Schedule

Edit `.github/workflows/daily-stock-analysis.yml`:

```yaml
schedule:
  - cron: '30 14 * * 1-5'  # Current: 9:30 AM EST, Mon-Fri
```

Cron format: `minute hour day month weekday`

Examples:
- `0 13 * * 1-5` - 9:00 AM EST, Mon-Fri
- `0 20 * * *` - 4:00 PM EST, Every day
- `0 9,15 * * 1-5` - 5:00 AM & 11:00 AM EST, Mon-Fri

### Add More Stocks

Edit `STOCK_SYMBOLS` list in `.github/workflows/stock_analyzer.py`:

```python
STOCK_SYMBOLS = [
    'AAPL', 'MSFT', 'YOUR_SYMBOL', ...
]
```

### Change AI Model

Edit the model in `stock_analyzer.py`:

```python
model="gpt-4o",  # Options: gpt-4o, gpt-4-turbo, gpt-3.5-turbo (cheaper)
```

## 💰 Cost Estimate

### OpenAI API:
- **GPT-4o**: ~$0.05-0.10 per analysis
- **Monthly** (20 trading days): ~$1-2/month
- **GPT-3.5-turbo** (cheaper alternative): ~$0.01 per analysis

### Email Service (Optional):
- **Mailgun**: Free tier (5,000 emails/month) - more than enough
- **SendGrid**: Free tier (12,000 emails/month)

**Total**: ~$1-2/month for OpenAI only

## 🧪 Testing

Run locally for testing:

```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export GITHUB_TOKEN="your-token"
export GITHUB_REPOSITORY="username/repo"

# Install dependencies
pip install -r .github/workflows/requirements.txt

# Run the script
python .github/workflows/stock_analyzer.py
```

## 📊 Example Output

```
TOP 5 STOCK PICKS - 2025-10-01
============================================================

Market Summary: Markets showing bullish momentum with tech sector
leading gains. Fed policy remains accommodative...

#1 - NVDA (NVIDIA Corporation)
  Price: $485.50 → Target: $550.00
  Risk: Medium | Horizon: Medium-term
  Reason: Strong AI chip demand, consistent revenue growth...

#2 - MSFT (Microsoft Corporation)
  Price: $378.20 → Target: $420.00
  Risk: Low | Horizon: Long-term
  Reason: Cloud growth acceleration, AI integration...

[... 3 more picks ...]

Strategy: Focus on tech leaders with AI exposure while maintaining
diversification across sectors...
============================================================
```

## ⚠️ Disclaimer

**This is automated analysis for informational purposes only.**

- NOT financial advice
- Always do your own research (DYOR)
- Consult with a licensed financial advisor
- Past performance doesn't guarantee future results
- Invest only what you can afford to lose

## 🐛 Troubleshooting

### Workflow fails with "Insufficient permissions"
→ Enable write permissions in Settings → Actions → General

### No email received
→ Check spam folder, verify Mailgun setup and secrets

### OpenAI API error
→ Verify API key is correct and has credits

### Stock data missing
→ Yahoo Finance API might be temporarily unavailable, will retry next day

## 📝 License

MIT License - Feel free to modify and use for your own purposes.

## 🤝 Contributing

Contributions welcome! Ideas:
- Add more data sources (Alpha Vantage, Polygon.io)
- Implement sentiment analysis from news
- Add technical indicators (RSI, MACD, etc.)
- Support for international markets
- Backtesting capabilities

---

**Built with:**
- [yfinance](https://github.com/ranaroussi/yfinance) - Stock data
- [OpenAI GPT-4](https://platform.openai.com/) - AI analysis
- [GitHub Actions](https://github.com/features/actions) - Automation
