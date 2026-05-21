#!/usr/bin/env python3
"""
Custom Stock Data Fetcher
Get real-time data for any NSE/BSE stock
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomStockFetcher:
    """Fetch and analyze any stock"""

    # Common NSE power stocks
    POWER_STOCKS = {
        'JPPOWERVNL.NS': 'Jaiprakash Power Ventures',
        'ADANIPOWER.NS': 'Adani Power',
        'NTPC.NS': 'NTPC Limited',
        'POWERGRID.NS': 'Power Grid Corporation',
        'TORNTPOWER.NS': 'Torrent Power',
        'RELIANCE.NS': 'Reliance Industries (Power division)',
    }

    def __init__(self):
        pass

    def get_stock_data(self, symbol: str, period: str = '3mo') -> dict:
        """Fetch stock data from yfinance"""
        try:
            logger.info(f"Fetching data for {symbol}...")

            # Download data
            data = yf.download(symbol, period=period, progress=False)

            if data.empty or len(data) < 5:
                logger.warning(f"No data found for {symbol}")
                return None

            # Calculate indicators
            result = self._analyze_stock(symbol, data)
            return result

        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None

    def _analyze_stock(self, symbol: str, data: pd.DataFrame) -> dict:
        """Analyze stock data"""

        close = data['Close']
        volume = data['Volume']

        # Latest values
        latest_price = close.iloc[-1]
        prev_close = close.iloc[-2] if len(close) > 1 else close.iloc[-1]

        # High/Low
        high_52w = close.max()
        low_52w = close.min()

        # Moving averages
        ma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) > 50 else None
        ma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) > 200 else None

        # Volume
        avg_volume = volume.iloc[-20:].mean()
        current_volume = volume.iloc[-1]

        # Change
        change = latest_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

        # RSI
        rsi = self._calculate_rsi(close)

        # MACD
        macd, signal = self._calculate_macd(close)

        return {
            'symbol': symbol,
            'latest_price': latest_price,
            'previous_close': prev_close,
            'change': change,
            'change_pct': change_pct,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 0,
            'rsi': rsi,
            'macd': macd,
            'signal': signal,
            'data': data
        }

    def _calculate_rsi(self, data: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        if len(data) < period + 1:
            return 50

        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def _calculate_macd(self, data: pd.Series) -> tuple:
        """Calculate MACD"""
        ema_12 = data.ewm(span=12).mean()
        ema_26 = data.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()

        return macd.iloc[-1], signal.iloc[-1]

    def display_stock_info(self, result: dict):
        """Display stock information"""
        if not result:
            print("No data available")
            return

        symbol = result['symbol']
        price = result['latest_price']
        change = result['change']
        change_pct = result['change_pct']

        status = "📈 UP" if change_pct > 0 else "📉 DOWN" if change_pct < 0 else "→ FLAT"

        print("\n" + "="*80)
        print(f"STOCK ANALYSIS - {symbol}")
        print("="*80)

        print("\n📊 PRICE INFORMATION:")
        print("-"*80)
        print(f"Current Price:        ₹{price:.2f}")
        print(f"Previous Close:       ₹{result['previous_close']:.2f}")
        print(f"Change:               {change:+.2f} ({change_pct:+.2f}%) {status}")

        print("\n📈 52-WEEK STATS:")
        print("-"*80)
        print(f"52-Week High:         ₹{result['high_52w']:.2f}")
        print(f"52-Week Low:          ₹{result['low_52w']:.2f}")
        print(f"Range:                ₹{result['low_52w']:.2f} - ₹{result['high_52w']:.2f}")

        print("\n📊 TECHNICAL INDICATORS:")
        print("-"*80)
        print(f"RSI (14):             {result['rsi']:.2f}")
        if 30 < result['rsi'] < 70:
            rsi_status = "Normal Trading Range"
        elif result['rsi'] < 30:
            rsi_status = "Oversold - Potential Bounce"
        else:
            rsi_status = "Overbought - Caution"
        print(f"RSI Status:           {rsi_status}")

        print(f"\nMACD:                 {result['macd']:.4f}")
        print(f"Signal Line:          {result['signal']:.4f}")
        if result['macd'] > result['signal']:
            macd_status = "Bullish Momentum"
        else:
            macd_status = "Bearish Momentum"
        print(f"MACD Status:          {macd_status}")

        if result['ma_50']:
            print(f"\n50-Day MA:            ₹{result['ma_50']:.2f}")
            ma50_status = "Above" if price > result['ma_50'] else "Below"
            print(f"Price vs MA50:        {ma50_status}")

        if result['ma_200']:
            print(f"200-Day MA:           ₹{result['ma_200']:.2f}")
            ma200_status = "Above" if price > result['ma_200'] else "Below"
            print(f"Price vs MA200:       {ma200_status}")

        print("\n📊 VOLUME:")
        print("-"*80)
        print(f"Current Volume:       {result['current_volume']:,.0f}")
        print(f"20-Day Avg Volume:    {result['avg_volume']:,.0f}")
        print(f"Volume Ratio:         {result['volume_ratio']:.2f}x")
        if result['volume_ratio'] > 1.5:
            volume_status = "High - Strong activity"
        else:
            volume_status = "Normal"
        print(f"Volume Status:        {volume_status}")

        print("\n" + "="*80)
        print(f"Last Updated:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

    def list_power_stocks(self):
        """List available power stocks"""
        print("\n" + "="*80)
        print("AVAILABLE POWER SECTOR STOCKS")
        print("="*80)
        print(f"{'Symbol':<20} {'Company Name':<40}")
        print("-"*80)

        for symbol, name in self.POWER_STOCKS.items():
            print(f"{symbol:<20} {name:<40}")

        print("-"*80)
        print("\nUsage:")
        print("  python fetch_custom_stock.py JPPOWERVNL.NS")
        print("  python fetch_custom_stock.py NTPC.NS")
        print("  python fetch_custom_stock.py ADANIPOWER.NS")
        print("="*80 + "\n")

def main():
    import sys

    fetcher = CustomStockFetcher()

    print("\n" + "🔋 "*20)
    print("CUSTOM STOCK DATA FETCHER - Power Sector Stocks")
    print("🔋 "*20)

    # Check if stock symbol provided
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()

        # Fetch data
        result = fetcher.get_stock_data(symbol, period='1y')

        if result:
            fetcher.display_stock_info(result)
        else:
            print(f"\n❌ Could not fetch data for {symbol}")
            print("\nTry one of these power stocks:")
            fetcher.list_power_stocks()
    else:
        # Show list of power stocks
        fetcher.list_power_stocks()

        print("\n💡 QUICK START:")
        print("-"*80)
        print("Get JP Power data:")
        print("  python fetch_custom_stock.py JPPOWERVNL.NS")
        print("\nGet NTPC data:")
        print("  python fetch_custom_stock.py NTPC.NS")
        print("\nGet any other stock (provide NSE symbol with .NS):")
        print("  python fetch_custom_stock.py SYMBOL.NS")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()
