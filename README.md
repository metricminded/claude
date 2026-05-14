# Intraday Trading Stock Analyzer

Daily automated stock scanner that identifies the top 3 NSE stocks to buy each morning, with technical analysis signals and email alerts.

## Features

✅ **Daily Analysis**: Analyzes 500+ liquid NSE stocks  
✅ **Technical Signals**: RSI, MACD, Moving Averages, Volume Analysis  
✅ **Email Alerts**: Morning notification with top 3 picks  
✅ **Scheduled Runs**: Automatic execution at 9:00 AM IST daily  
✅ **Scoring System**: Stocks ranked by 7-point technical score  

## How It Works

1. **Stock Analyzer** (`stock_analyzer.py`)
   - Fetches 90 days of historical data for 500+ NSE stocks
   - Calculates technical indicators:
     - RSI (Relative Strength Index)
     - MACD (Moving Average Convergence Divergence)
     - 50-day & 200-day Moving Averages
     - Volume Analysis (vs. 20-day average)
     - Gap Up Detection
   - Scores each stock (0-7 points)
   - Returns top 3 picks

2. **Email Notifier** (`notifier.py`)
   - Sends formatted HTML email with:
     - Stock symbols & prices
     - Technical scores & signals
     - Reason to buy
     - Risk disclaimer

3. **Scheduler** (`scheduler.py`)
   - Runs automatically at 9:00 AM IST
   - Keeps running in background
   - Logs all activity

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email (Gmail)

**Important**: For security, use an App Password, not your Gmail password.

**Steps to create Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication (if not already enabled)
3. Go to "App passwords" 
4. Select "Mail" and "Windows Computer" (or your device)
5. Google generates a 16-character password
6. Copy this password

### 3. Create Configuration File

```bash
cp config.json.template config.json
```

Edit `config.json`:
```json
{
  "email": {
    "sender": "your-email@gmail.com",
    "password": "your-16-char-app-password",
    "recipient": "your-email@gmail.com"
  },
  "scheduler": {
    "run_time": "09:00",
    "timezone": "Asia/Kolkata"
  },
  "analysis": {
    "stocks_to_analyze": 500,
    "top_picks": 3,
    "lookback_days": 90
  }
}
```

### 4. Test the Analyzer

Run once manually to test:

```bash
python stock_analyzer.py
```

You should see output like:
```
============================================================
TOP 3 STOCKS TO BUY TODAY
============================================================

1. RELIANCE.NS
   Price: ₹2456.50
   Score: 6/7
   RSI: 42.3
   Signals:
     • RSI in trading range (42.3)
     • MACD bullish crossover
     • Volume spike (2.3x avg)
```

### 5. Start the Scheduler

```bash
python scheduler.py
```

The scheduler will:
- Run daily at 9:00 AM IST
- Send email with top 3 stocks
- Log results to `stock_analyzer.log`
- Keep running in background

## Running in Background (Linux/Mac)

### Using nohup:
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

### Using systemd (Linux):
Create `/etc/systemd/system/stock-analyzer.service`:
```ini
[Unit]
Description=Stock Analyzer
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/user/claude
ExecStart=/usr/bin/python3 /home/user/claude/scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable stock-analyzer
sudo systemctl start stock-analyzer
```

### Using cron:
```bash
crontab -e
```

Add line:
```
0 9 * * * /usr/bin/python3 /home/user/claude/scheduler.py >> /home/user/claude/cron.log 2>&1
```

## Customization

### Change Analysis Time
Edit `scheduler.py`:
```python
schedule.every().day.at("08:00").do(run_daily_analysis)  # 8:00 AM IST
```

### Add More Stocks to Analyze
Edit `stock_analyzer.py` in `_get_top_nse_stocks()` method:
```python
top_stocks = [
    'RELIANCE.NS', 'TCS.NS', 'INFOSY.NS',
    # ... add more symbols
]
```

### Adjust Scoring Criteria
Edit `analyze_stock()` in `stock_analyzer.py` to change how points are awarded based on indicators.

### Change Email Recipients
Edit `notifier.py` or update `config.json`:
```json
"email": {
  "recipient": "multiple@emails.com,another@email.com"
}
```

## Understanding the Signals

| Signal | What It Means | Trading Implication |
|--------|---------------|-------------------|
| **RSI < 30** | Stock is oversold | Potential bounce/reversal |
| **RSI 30-70** | Healthy trading range | Normal momentum |
| **MACD Bullish Crossover** | Momentum turning positive | Uptrend starting |
| **Price > 200-day MA** | Long-term uptrend | In established uptrend |
| **Volume Spike** | Unusual buying activity | Strong conviction move |
| **Gap Up** | Positive opening | Strong sentiment |

## Important Disclaimers

⚠️ **THIS IS NOT FINANCIAL ADVICE**

- Technical analysis is not guaranteed to predict future price movements
- Past performance does not guarantee future results
- Intraday trading involves HIGH RISK
- You can lose your entire capital
- Always use stop losses
- Never risk more than you can afford to lose
- Do your own research before trading
- Consider consulting a financial advisor

## Troubleshooting

### Email not sending?
- Check Gmail app password (not regular password)
- Verify email addresses in config.json
- Check internet connection
- Look at logs: `cat stock_analyzer.log`

### Stock data not downloading?
- Check internet connection
- Yahoo Finance might be temporarily unavailable
- Try manually: `python -c "import yfinance; print(yfinance.download('RELIANCE.NS', period='1d'))"`

### Scheduler not running?
- Make sure you're running Python 3.7+
- Check logs: `tail -f stock_analyzer.log`
- Verify config.json exists and is valid JSON

## Performance Tips

- Run at 9:00 AM (after market opens) for most current data
- First run takes longer (analyzing 500 stocks)
- Email sending adds ~10-20 seconds
- Consider running on a cloud server (AWS, DigitalOcean, etc.) for 24/7 execution

## License

Use at your own risk. This is educational software for personal use.

---

**Questions or Issues?**  
Review the logs and ensure all configuration steps are followed correctly.

**Last Updated**: 2024
