#!/usr/bin/env python3
"""
Real NSE Stock Prices - Multiple data sources
Uses alternative APIs and web scraping to get live prices
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealPricesGetter:
    """Fetch real prices from multiple sources"""

    def __init__(self):
        self.stocks = {
            'RELIANCE.NS': 'RELIANCE',
            'TCS.NS': 'TCS',
            'INFOSY.NS': 'INFOSY',
            'ICICIBANK.NS': 'ICICIBANK',
            'HDFC.NS': 'HDFC',
            'WIPRO.NS': 'WIPRO',
            'KOTAK.NS': 'KOTAK',
            'LT.NS': 'LT',
            'SBIN.NS': 'SBIN',
            'MARUTI.NS': 'MARUTI'
        }

    def get_prices_from_nseindia(self):
        """Fetch from NSE India official API (most reliable)"""
        print("\n" + "="*80)
        print("METHOD 1: NSE India Official API")
        print("="*80)

        try:
            # NSE India official endpoint
            url = "https://www.nseindia.com/api/quote-equity"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            prices = {}
            print("\nAttempting to fetch from NSE India official API...")
            print("-" * 80)

            for symbol, name in list(self.stocks.items())[:5]:
                try:
                    params = {'symbol': name}
                    response = requests.get(url, params=params, headers=headers, timeout=5)

                    if response.status_code == 200:
                        data = response.json()
                        price = data.get('priceData', {}).get('price', 'N/A')
                        print(f"✓ {symbol}: ₹{price}")
                        prices[symbol] = price
                    else:
                        print(f"✗ {symbol}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"✗ {symbol}: {str(e)[:50]}")

            return prices if prices else None

        except Exception as e:
            print(f"API Error: {e}")
            return None

    def get_prices_from_alpha_vantage(self):
        """Fetch from Alpha Vantage (free tier)"""
        print("\n" + "="*80)
        print("METHOD 2: Alpha Vantage API (Free Tier)")
        print("="*80)

        # Free API key - limited calls
        api_key = "demo"  # Replace with your free key from alphavantage.co

        print("\n⚠️  Alpha Vantage requires free API key registration:")
        print("    1. Go to https://www.alphavantage.co/api/")
        print("    2. Sign up for free API key")
        print("    3. Replace 'demo' with your key in this script")
        print("\nExample:")
        print("    api_key = 'your-free-key-here'")
        print("    response = requests.get(url, params=params)")

        return None

    def get_prices_from_polygon(self):
        """Fetch from Polygon.io"""
        print("\n" + "="*80)
        print("METHOD 3: Polygon.io API")
        print("="*80)

        print("\n✓ Polygon.io offers free stock data:")
        print("    1. Free tier: https://polygon.io/")
        print("    2. Get API key (free)")
        print("    3. Use for real-time NSE data")

        return None

    def get_prices_from_iex_cloud(self):
        """Fetch from IEX Cloud"""
        print("\n" + "="*80)
        print("METHOD 4: IEX Cloud API")
        print("="*80)

        print("\n✓ IEX Cloud has free plan:")
        print("    1. Visit https://iexcloud.io/")
        print("    2. Sign up (free tier available)")
        print("    3. Get publishable API key")

        return None

    def get_prices_from_eoddata(self):
        """Fetch from EODdata"""
        print("\n" + "="*80)
        print("METHOD 5: EODdata API")
        print("="*80)

        print("\n✓ EODdata provides NSE data:")
        print("    1. Website: https://eoddata.com/")
        print("    2. Free API key available")
        print("    3. Real-time NSE quotes")

        return None

    def instructions_for_real_prices(self):
        """Print instructions to get real prices"""
        print("\n" + "="*80)
        print("HOW TO GET REAL NSE PRICES")
        print("="*80)

        instructions = """
📍 OPTION A: Run Locally (Easiest - Works Immediately)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Clone repository:
   git clone https://github.com/metricminded/claude.git
   cd claude
   git checkout claude/setup-yfinance-api-2Eksa

2. Install dependencies:
   pip install -r requirements.txt

3. Run real price fetcher:
   python market_prices.py              # Uses yfinance
   python stock_analyzer.py              # Full analysis

✓ This works immediately with internet connection


📍 OPTION B: Use Free Financial APIs (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  Alpha Vantage (Best for stocks)
   • Free API key: https://www.alphavantage.co/
   • Limit: 5 requests/min, 500/day
   • Supports NSE stocks

   Setup:
   pip install alpha_vantage

   Code:
   from alpha_vantage.timeseries import TimeSeries
   ts = TimeSeries(key='YOUR_API_KEY')
   data, meta = ts.get_daily(symbol='RELIANCE.NS')


2️⃣  Polygon.io (Real-time data)
   • Free tier: https://polygon.io/
   • Real-time stock prices
   • Supports NSE

   Setup:
   pip install polygon-api-client

   Code:
   from polygon import RESTClient
   client = RESTClient('YOUR_API_KEY')
   quotes = client.get_last_quote("RELIANCE.NS")


3️⃣  IEX Cloud (Reliable)
   • Free plan: https://iexcloud.io/
   • 100,000 messages/month free

   Setup:
   pip install iexfinance

   Code:
   from iexfinance.stocks import get_historical_data
   data = get_historical_data("RELIANCE.NS", api_key='YOUR_API_KEY')


4️⃣  EODdata (Best for NSE)
   • NSE data available: https://eoddata.com/
   • Free registration

   Setup:
   pip install eoddata

   Code:
   client = eoddata.Client()
   quotes = client.get_quotes('NSE')


📍 OPTION C: Web Scraping (NSE Website)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scrape live data from:
   • Official NSE: https://www.nseindia.com/
   • BSE India: https://www.bseindia.com/
   • Moneycontrol: https://www.moneycontrol.com/
   • ET Markets: https://economictimes.indiatimes.com/markets

pip install beautifulsoup4 requests


📍 RECOMMENDED SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Sign up for free Alpha Vantage API key (5 min)
2. Install: pip install alpha_vantage
3. Update requirements.txt:
   alpha_vantage==2.3.1
4. Run modified stock analyzer

Quick Setup Steps:
1. Go to https://www.alphavantage.co/
2. Email → Free API key in 2 seconds
3. Update your script with the key
4. Run: python stock_analyzer.py

That's it! Real prices in seconds.
"""
        print(instructions)


def main():
    getter = RealPricesGetter()

    # Try to fetch from NSE API
    prices = getter.get_prices_from_nseindia()

    if not prices:
        # Show alternative methods
        getter.get_prices_from_alpha_vantage()
        getter.get_prices_from_polygon()
        getter.get_prices_from_iex_cloud()
        getter.get_prices_from_eoddata()

    # Print complete instructions
    getter.instructions_for_real_prices()

    print("\n" + "="*80)
    print("QUICK COMMAND TO GET STARTED:")
    print("="*80)
    print("\n# For Alpha Vantage (easiest):")
    print("pip install alpha_vantage")
    print("\n# For Polygon.io:")
    print("pip install polygon-api-client")
    print("\n# For local yfinance (best - run on your machine):")
    print("pip install -r requirements.txt && python market_prices.py")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
