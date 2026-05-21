# 🚀 Zerodha Kite Connect Setup Guide

Complete guide to setting up Kite Connect for real NSE data.

---

## 💰 Cost & Requirements

| Item | Cost | Note |
|------|------|------|
| **Zerodha Demat Account** | ₹200 (one-time) | Required |
| **Kite Connect API** | ₹2,000/month | The API subscription |
| **Total Monthly** | **₹2,000** | After demat opens |

---

## 📋 Step-by-Step Setup

### Step 1: Open Zerodha Demat Account (If you don't have one)

1. Visit: https://zerodha.com/
2. Click "Sign Up"
3. Complete KYC (takes 1-2 days)
4. Cost: ₹200 (one-time charge)

### Step 2: Subscribe to Kite Connect

1. Login to: https://developers.kite.trade/
2. Create a new app:
   - **App Name:** TimesFM Trading System
   - **App Type:** Personal
   - **Redirect URL:** `http://127.0.0.1:5000/callback`
3. Get your **API Key** and **API Secret**
4. Subscribe for ₹2,000/month

### Step 3: Install Kite Connect Python Library

```bash
pip install kiteconnect
```

Already in requirements.txt - just run:
```bash
pip install -r requirements.txt
```

### Step 4: Authenticate (One Time Daily)

```bash
python kite_connect_integration.py auth
```

You'll see:
```
🔐 KITE CONNECT AUTHENTICATION
======================================
Enter your Kite API Key: <paste here>
Enter your Kite API Secret: <paste here>

📋 Step 1: Open this URL in browser:
   https://kite.zerodha.com/connect/login?...

📋 Step 2: Login with Zerodha credentials
📋 Step 3: After login, copy 'request_token' from URL
   (URL will look like: http://127.0.0.1:5000/callback?request_token=ABC123)

Enter request_token from redirect URL: ABC123

✅ SUCCESS!
Access Token: xyz789...
```

### Step 5: Set Environment Variables

Add to your `.bashrc` or `.zshrc`:
```bash
export KITE_API_KEY='your_api_key_here'
export KITE_ACCESS_TOKEN='your_access_token_here'
```

Or create `.env` file:
```
KITE_API_KEY=your_api_key_here
KITE_ACCESS_TOKEN=your_access_token_here
```

### Step 6: Run Backtest with Real Data!

```bash
python kite_connect_integration.py backtest
```

---

## ⚠️ Important: Daily Token Refresh

Kite Connect access tokens **expire every day at 6:00 AM IST**.

You need to re-authenticate daily:

### Manual Daily Auth
```bash
python kite_connect_integration.py auth
```

### Automated Daily Auth (Advanced)
Create `daily_auth.sh`:
```bash
#!/bin/bash
# Run at 6:01 AM daily via cron
python /path/to/kite_connect_integration.py auth_automated
```

Add to crontab:
```bash
1 6 * * * /path/to/daily_auth.sh
```

---

## 🎯 Usage Examples

### Get Historical Data

```python
from kite_connect_integration import KiteDataProvider

kite = KiteDataProvider()

# Get 90 days of daily data
df = kite.get_historical_data('RELIANCE', days=90)
print(df.head())

# Output:
#                       open    high     low   close   volume
# date
# 2026-02-21      2440.50  2455.00 2435.20 2450.00  1234567
# ...
```

### Get Current Price (Real-time)

```python
ltp = kite.get_current_price('JPOWER')
print(f"JP Power LTP: ₹{ltp}")

# Output: JP Power LTP: ₹18.56
```

### Get Full Quote

```python
quote = kite.get_quote('RELIANCE')
print(quote)

# Output:
# {
#   'last_price': 2450.00,
#   'volume': 12345678,
#   'buy_quantity': 5000,
#   'sell_quantity': 7000,
#   'ohlc': {...},
#   ...
# }
```

### Get Intraday Data

```python
# 5-minute candles
df = kite.get_historical_data('JPOWER', days=5, interval='5minute')

# 15-minute candles  
df = kite.get_historical_data('JPOWER', days=10, interval='15minute')
```

---

## 📊 Available Intervals

| Interval | Use Case |
|----------|----------|
| `minute` | High-frequency trading |
| `3minute` | Scalping |
| `5minute` | Intraday trading ⭐ |
| `15minute` | Day trading |
| `30minute` | Swing trading |
| `60minute` | Position trading |
| `day` | Backtesting ⭐ |

---

## 🔐 Security Best Practices

### Never Commit Credentials!

Add to `.gitignore`:
```
.env
.kite_token
config_kite.json
```

### Use Environment Variables

```bash
# In your shell config (.bashrc, .zshrc)
export KITE_API_KEY="your_key"
export KITE_API_SECRET="your_secret"
export KITE_ACCESS_TOKEN="your_token"
```

### Use Config File (Local Only)

`config_kite.json`:
```json
{
  "api_key": "your_key",
  "api_secret": "your_secret",
  "redirect_url": "http://127.0.0.1:5000/callback"
}
```

Load in code:
```python
with open('config_kite.json') as f:
    config = json.load(f)
kite = KiteDataProvider(api_key=config['api_key'])
```

---

## ⚡ Real-Time Trading (Advanced)

Once authenticated, you can also place real orders!

```python
# Place a buy order
order_id = kite.kite.place_order(
    variety='regular',
    exchange='NSE',
    tradingsymbol='JPOWER',
    transaction_type='BUY',
    quantity=100,
    product='MIS',  # Intraday
    order_type='LIMIT',
    price=18.50,
)

# Set stop loss
sl_order = kite.kite.place_order(
    variety='regular',
    exchange='NSE',
    tradingsymbol='JPOWER',
    transaction_type='SELL',
    quantity=100,
    product='MIS',
    order_type='SL',
    price=18.40,
    trigger_price=18.42,
)
```

**⚠️ WARNING:** This will place REAL orders with REAL money!
- Start with paper trading
- Test with small quantities first
- Always have stop losses
- Monitor positions actively

---

## 🐛 Troubleshooting

### Error: "Invalid api_key or api_secret"
**Fix:** Double-check credentials at https://developers.kite.trade/

### Error: "Token is invalid or has expired"
**Fix:** Re-authenticate (tokens expire daily at 6 AM IST)
```bash
python kite_connect_integration.py auth
```

### Error: "Insufficient funds"
**Fix:** Check available margin in Zerodha account

### Error: "Order rejected"
**Common reasons:**
- Market closed (NSE: 9:15 AM - 3:30 PM IST)
- Stock in upper/lower circuit
- Invalid quantity (must be in lot sizes)

---

## 💰 Cost vs Value Analysis

### Monthly Cost: ₹2,000

### What You Get:
- ✅ Real-time NSE & BSE data
- ✅ Historical data (years of backtesting)
- ✅ Order placement API
- ✅ Portfolio management
- ✅ 99.9% uptime
- ✅ Official Zerodha support
- ✅ No rate limits for personal use

### When It's Worth It:
- ✅ Trading daily (>20 trades/month)
- ✅ Need real-time data
- ✅ Want to automate trades
- ✅ Backtesting strategies seriously

### When It's NOT Worth It:
- ❌ Just learning/testing (use Upstox FREE)
- ❌ Trading rarely
- ❌ Only need EOD data

---

## 🆚 Comparison with Alternatives

| Feature | Kite Connect (₹2k/mo) | Upstox (FREE) | yfinance (FREE) |
|---------|----------------------|----------------|-----------------|
| Real-time data | ✅ Yes | ✅ Yes | ❌ Delayed |
| Historical data | ✅ Years | ✅ Years | ✅ Years |
| Order placement | ✅ Yes | ✅ Yes | ❌ No |
| Reliability | 99.9% | 99% | Variable |
| Support | Official | Official | Community |
| Rate limits | None | Limited | None |
| Setup difficulty | Medium | Medium | Easy |

---

## 🚀 Quick Start

```bash
# 1. Install
pip install kiteconnect

# 2. Authenticate (daily)
python kite_connect_integration.py auth

# 3. Run backtest with REAL data
python kite_connect_integration.py backtest

# 4. View results
ls -lrt backtest_results/
```

---

## 📚 Resources

- **Kite Connect Docs:** https://kite.trade/docs/connect/v3/
- **API Pricing:** https://kite.trade/
- **Developer Console:** https://developers.kite.trade/
- **Community Forum:** https://kite.trade/forum/
- **Python Library:** https://github.com/zerodha/pykiteconnect

---

## ✅ Setup Checklist

- [ ] Zerodha Demat account opened
- [ ] Kite Connect app created
- [ ] API Key & Secret obtained
- [ ] kiteconnect Python library installed
- [ ] First authentication completed
- [ ] Environment variables set
- [ ] Test data fetched successfully
- [ ] Backtest run with real data
- [ ] Daily auth automated (optional)

---

**You're ready to trade with real NSE data!** 🎯

Cost: ₹2,000/month
Benefit: Professional-grade trading data
Expected ROI: 10-30% monthly (if strategy works)

Break-even: Make ₹2,000+ profit/month to cover API cost.
