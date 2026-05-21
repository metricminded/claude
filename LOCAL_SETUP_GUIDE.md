# Local Setup Guide - Run NSE Stock Analyzer on Your Machine

## ⚡ Super Quick Start (30 seconds)

### On Mac/Linux:
```bash
# Copy and paste this entire command:
git clone https://github.com/metricminded/claude.git && cd claude && git checkout claude/setup-yfinance-api-2Eksa && pip install -r requirements.txt && python market_prices.py
```

### On Windows (PowerShell):
```powershell
# Copy and paste this entire command:
git clone https://github.com/metricminded/claude.git; cd claude; git checkout claude/setup-yfinance-api-2Eksa; pip install -r requirements.txt; python market_prices.py
```

---

## 📋 Step-by-Step Setup

### Prerequisites
- ✅ Python 3.7+ installed ([Download](https://www.python.org/downloads/))
- ✅ Git installed ([Download](https://git-scm.com/))
- ✅ Internet connection
- ✅ Terminal/Command Prompt access

### Step 1: Clone Repository (1 min)

**Mac/Linux:**
```bash
git clone https://github.com/metricminded/claude.git
cd claude
```

**Windows (Command Prompt or PowerShell):**
```cmd
git clone https://github.com/metricminded/claude.git
cd claude
```

### Step 2: Checkout Branch (30 sec)

```bash
git checkout claude/setup-yfinance-api-2Eksa
```

**Output should show:**
```
Switched to branch 'claude/setup-yfinance-api-2Eksa'
```

### Step 3: Create Virtual Environment (1 min)

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Verify activation:** Your prompt should show `(venv)` prefix

### Step 4: Install Dependencies (2 min)

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**This installs:**
```
✓ yfinance==0.2.40
✓ pandas==2.0.3
✓ numpy==1.24.3
✓ schedule==1.2.0
```

### Step 5: Configure (1 min)

Edit `config.json`:

**Mac/Linux:**
```bash
nano config.json
# or use your editor
```

**Windows:**
```cmd
notepad config.json
```

Update your email:
```json
{
  "email": {
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

---

## ✅ Test Your Setup

### Run Tests
```bash
python test.py
```

**Expected output:**
```
============================================================
Stock Analyzer Setup Test
============================================================

[Imports]
✓ All packages imported successfully

[Config]
✓ Config file valid

[Analyzer]
✓ Analyzer working - found X stocks

============================================================
✓ All tests passed!
```

### If tests fail:
1. Check internet connection
2. Verify Python 3.7+: `python --version`
3. Verify pip installed deps: `pip list | grep yfinance`
4. Try again: `python test.py`

---

## 💹 Get Real Prices

### Command 1: View Current Market
```bash
python market_prices.py
```

**Output:**
```
================================================================================
LIVE NSE MARKET PRICES - INDIA
================================================================================
📊 Timestamp: 2026-05-21 04:59:07 IST
================================================================================
Stock           Current         Prev Close      Change       Change %   Status    
------------------------------------------------------------------------------------------
RELIANCE.NS     ₹2875.50       ₹2856.25          +19.25      0.67% 📈 UP      
TCS.NS          ₹4125.80       ₹4098.50          +27.30      0.67% 📈 UP      
ICICIBANK.NS    ₹1158.90       ₹1145.75          +13.15      1.15% 📈 UP      
[... more stocks ...]
```

### Command 2: Get Stock Analysis
```bash
python stock_analyzer.py
```

**Output:**
```
============================================================
TOP 3 STOCKS TO BUY TODAY
============================================================

1. RELIANCE.NS
   Price: ₹2875.50
   Score: 6/7
   RSI: 42.3
   Signals:
     • RSI in trading range (42.3)
     • MACD bullish crossover
     • Volume spike (2.3x avg)

2. TCS.NS
   [...]

Disclaimer: This is technical analysis only.
Do your own research before trading.
```

### Command 3: Demo (If Market is Closed)
```bash
python stock_analyzer_demo.py
```

Uses sample data - perfect for testing offline

---

## ⏰ Run Daily Scheduler

### Start Automatic Analysis
```bash
python scheduler.py
```

**This will:**
- Run analysis at 9:00 AM IST every day
- Analyze 500 NSE stocks
- Find top 3 picks
- Save email ready to send

**To stop:** Press `Ctrl+C`

### Run in Background (Continuous)

**Mac/Linux:**
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

Check logs:
```bash
tail -f scheduler.log
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Set action: Run `python scheduler.py`

---

## 💌 Send Email Alerts

After scheduler runs and finds stocks:

```bash
python send_email.py
```

This shows you the email data. To send it via Gmail MCP connector (integrated with Claude Code), use the `create_draft` tool in Claude.

---

## 🔄 Daily Workflow

### Option A: Manual (Run anytime)
```bash
# Activate environment
source venv/bin/activate  # Mac/Linux
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Get prices
python market_prices.py

# Analyze
python stock_analyzer.py

# Send alerts (optional)
python send_email.py
```

### Option B: Automated (Set and forget)
```bash
python scheduler.py
```

Runs every day at 9:00 AM IST automatically.

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'yfinance'"
**Solution:**
```bash
# Make sure virtual environment is activated
# (should see (venv) in your prompt)
pip install -r requirements.txt
```

### "Failed to get ticker" / "No data"
**Causes:**
- Market is closed (9:15 AM - 3:30 PM IST only)
- Internet connection issue
- Yahoo Finance rate limit hit

**Solutions:**
```bash
# Try demo instead
python stock_analyzer_demo.py

# Wait a minute and try again
# Run during market hours
```

### "Connection refused"
**Solutions:**
1. Check internet: `ping google.com`
2. Try with demo: `python stock_analyzer_demo.py`
3. Check firewall settings
4. Try VPN if geo-blocked

### "config.json not found"
**Solution:**
```bash
cp config.json.template config.json
# Then edit with your email
nano config.json
```

### Python version too old
**Solution:**
```bash
# Check version
python --version

# If < 3.7, install latest from https://www.python.org/downloads/
# Then try again
python3 --version
python3 -m venv venv
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `market_prices.py` | View current NSE prices |
| `stock_analyzer.py` | Analyze & find top 3 stocks |
| `scheduler.py` | Run daily at 9:00 AM IST |
| `config.json` | Your settings (email, time, etc) |
| `stock_analyzer.log` | Log of all analyses |
| `requirements.txt` | Python packages to install |

---

## 🎯 Next Steps

1. ✅ **Setup Complete** - You have everything running
2. 📊 **Get Prices** - Run `python market_prices.py` anytime
3. 📈 **Analyze** - Run `python stock_analyzer.py` for top picks
4. 📅 **Automate** - Run `python scheduler.py` for daily alerts
5. 💌 **Notify** - Use email feature to send alerts

---

## 📚 Additional Commands

```bash
# Test everything
python test.py

# View logs (while running)
tail -f stock_analyzer.log

# Check what stocks are analyzed
grep "Found" stock_analyzer.log

# View cached email
cat email_metadata.json

# Stop scheduler (Ctrl+C in terminal)
# On Mac/Linux to kill background process:
pkill -f scheduler.py

# On Windows to kill:
taskkill /im python.exe /f
```

---

## 💡 Pro Tips

1. **Best Time**: Run at 9:30 AM IST (after market opens) for fresh data
2. **Daily**: Set scheduler to run automatically
3. **Testing**: Use demo mode offline
4. **Logs**: Check `stock_analyzer.log` for errors
5. **Background**: Use `nohup` on Mac/Linux to keep running

---

## ✨ You're All Set!

Run this command right now to see live NSE prices:

```bash
cd claude && python market_prices.py
```

**That's it! Real NSE prices in your terminal! 🚀**

---

## 📞 Support

If something goes wrong:
1. Run `python test.py` to diagnose
2. Check `stock_analyzer.log` for errors
3. Try `python stock_analyzer_demo.py` to test logic
4. Verify Python 3.7+: `python --version`
5. Verify internet connection

---

**Happy trading! Remember: This is analysis only, not financial advice. Always do your own research! 📚**
