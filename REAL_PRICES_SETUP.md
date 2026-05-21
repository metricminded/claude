# Getting Real NSE Stock Prices

## Quick Start (3 Steps - 5 Minutes)

### Step 1: Get Free API Key
1. Go to: https://www.alphavantage.co/
2. Enter your email
3. Get API key instantly (sent to email)

### Step 2: Install Library
```bash
pip install alpha_vantage
```

### Step 3: Use Real Prices
```bash
# Set your API key
export ALPHA_VANTAGE_API_KEY="your-api-key-here"

# Get real prices
python alpha_vantage_prices.py
```

---

## Option 1: Alpha Vantage (Recommended)
**Best for:** NSE stocks, free, easy setup

```bash
# Install
pip install alpha_vantage

# Get API key from https://www.alphavantage.co/
# Free tier: 500 calls/day, 5 calls/min

# Usage
python alpha_vantage_prices.py
```

**Features:**
- ✅ Real-time NSE prices
- ✅ Historical data
- ✅ Technical indicators
- ✅ Free tier suitable for daily analysis

---

## Option 2: Polygon.io
**Best for:** Real-time data, multiple markets

```bash
# Install
pip install polygon-api-client

# Get free API key from https://polygon.io/
# Free tier: 5 API calls/min

# Usage
python polygon_prices.py
```

---

## Option 3: IEX Cloud
**Best for:** Reliable, professional data

```bash
# Install
pip install iexfinance

# Get free API key from https://iexcloud.io/
# Free tier: 100,000 messages/month

# Usage
python iex_prices.py
```

---

## Option 4: Run Locally (Best)
**Best for:** Zero API limitations, instant data**

Run on your computer where you have internet:

```bash
# Clone repo
git clone https://github.com/metricminded/claude.git
cd claude
git checkout claude/setup-yfinance-api-2Eksa

# Install
pip install -r requirements.txt

# Get real prices using yfinance
python market_prices.py
```

---

## Complete Implementation Examples

### Alpha Vantage Example
```python
from alpha_vantage.timeseries import TimeSeries
import os

# Get API key from environment
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

# Initialize
ts = TimeSeries(key=api_key, output_format='pandas')

# Get daily data
data, meta_data = ts.get_daily(symbol='RELIANCE.NS')

# Latest price
latest_price = data['4. close'].iloc[0]
print(f"RELIANCE.NS: ₹{latest_price:.2f}")
```

### Polygon.io Example
```python
from polygon import RESTClient

# Get API key from environment
api_key = os.getenv('POLYGON_API_KEY')

# Initialize
client = RESTClient(api_key)

# Get latest quote
quote = client.get_last_quote('RELIANCE.NS')
print(f"RELIANCE.NS: ₹{quote.bid}")
```

### IEX Cloud Example
```python
from iexfinance.stocks import Stock

# Get API key from environment
api_key = os.getenv('IEX_API_KEY')

# Get stock
stock = Stock('RELIANCE.NS', token=api_key)
price = stock.get_price()
print(f"RELIANCE.NS: ₹{price}")
```

---

## Comparison Table

| Feature | Alpha Vantage | Polygon.io | IEX Cloud | Local (yfinance) |
|---------|---|---|---|---|
| Free Tier | ✅ 500/day | ✅ Limited | ✅ 100K/month | ✅ Unlimited |
| NSE Support | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Real-time | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Setup Time | 2 min | 2 min | 2 min | 1 min |
| API Calls | 5/min | 5/min | High | Unlimited |
| Best For | Daily analysis | Trading | Production | Development |

---

## Troubleshooting

**"Connection refused"**
- Check internet connection
- Verify API key is correct
- Check API rate limits

**"Invalid API Key"**
- Generate new key from provider website
- Make sure you're using the right key for the right API

**"No data returned"**
- Some APIs have delayed NSE data (15-20 min delay)
- Try with US stocks first to test connection
- Check if market is open (9:15 AM - 3:30 PM IST)

---

## Next Steps

1. **Choose one API** (Alpha Vantage recommended for ease)
2. **Get free API key** (2 minutes)
3. **Update your scripts** with the key
4. **Run the analyzer** with real prices
5. **Set up scheduler** for daily alerts

---

## Environment Variables Setup

### On Linux/Mac:
```bash
# Add to ~/.bashrc or ~/.zshrc
export ALPHA_VANTAGE_API_KEY="your-key-here"
export POLYGON_API_KEY="your-key-here"
export IEX_API_KEY="your-key-here"

# Reload
source ~/.bashrc
```

### On Windows (PowerShell):
```powershell
$env:ALPHA_VANTAGE_API_KEY="your-key-here"
$env:POLYGON_API_KEY="your-key-here"
$env:IEX_API_KEY="your-key-here"
```

---

**Questions?** Check the official documentation:
- Alpha Vantage: https://www.alphavantage.co/documentation/
- Polygon.io: https://polygon.io/docs/stocks
- IEX Cloud: https://iexcloud.io/docs/api/
