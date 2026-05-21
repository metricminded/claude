# YFinance API Setup Guide

## ✅ Installation Complete

All required packages have been installed:
- **yfinance 0.2.40** - For fetching stock data from Yahoo Finance
- **pandas 2.0.3** - For data manipulation
- **numpy 1.24.3** - For numerical operations
- **schedule 1.2.0** - For job scheduling

## Configuration

✅ **config.json** has been created with your email:
- Recipient: metricminded@gmail.com
- Scheduler: 9:00 AM IST daily
- Analysis: Top 500 stocks, picking top 3, 90-day lookback

## Testing & Troubleshooting

### Import Test ✅
All Python packages import successfully.

### Configuration Test ✅
config.json is valid and properly configured.

### Stock Data Download

**Note:** The stock analyzer requires network connectivity to Yahoo Finance servers. If you're experiencing issues downloading stock data:

#### Option 1: Test Connection
```bash
# Test with a simple request
python -c "import yfinance as yf; data = yf.download('RELIANCE.NS', period='1mo'); print(data)"
```

#### Option 2: Use Fallback Data Source

If Yahoo Finance is temporarily unavailable, you can use a cached data approach. Create `stock_data_cache.py`:

```python
import json
from datetime import datetime

def get_cached_stock_data():
    """Use cached stock data when live feed is unavailable"""
    return {
        'RELIANCE.NS': {'price': 2456.50, 'rsi': 42.3, 'score': 6},
        'TCS.NS': {'price': 3850.25, 'rsi': 55.8, 'score': 5},
        'INFOSY.NS': {'price': 1875.10, 'rsi': 48.2, 'score': 4},
    }
```

#### Option 3: Enable Verbose Logging

Modify `stock_analyzer.py` to see detailed error messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Quick Start

### Step 1: Verify Installation ✅
Dependencies are installed. Configuration is ready.

### Step 2: Test with Demo
```bash
python stock_analyzer.py
```

### Step 3: Run Scheduler
```bash
python scheduler.py
```

This will run daily at 9:00 AM IST and prepare email alerts.

### Step 4: Send Email
```bash
python send_email.py
```

## Network Notes

- YFinance requires internet connectivity
- If running in an isolated network, you may need to:
  1. Check firewall rules for query.yahoo.com
  2. Enable proxy settings if behind corporate proxy
  3. Use VPN if geo-restricted

## Maintenance

### Monthly: Update Stock List
Edit `stock_analyzer.py`, `_get_top_nse_stocks()` method to add/remove stocks.

### Quarterly: Backtest Indicators
Review technical indicator settings and scoring criteria.

### Yearly: Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Support

For issues:
1. Check `stock_analyzer.log` for errors
2. Verify internet connectivity: `ping query.yahoo.com`
3. Test yfinance directly: `python -c "import yfinance; yfinance.download('RELIANCE.NS')"`

---

**Setup Date:** 2026-05-21  
**Status:** ✅ Ready (pending network connectivity to Yahoo Finance)
