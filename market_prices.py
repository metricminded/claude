#!/usr/bin/env python3
"""
Real-time market prices fetcher
Displays current NSE stock prices with live data
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketPrices:
    def __init__(self):
        self.stocks = [
            'RELIANCE.NS', 'TCS.NS', 'INFOSY.NS', 'ICICIBANK.NS', 'HDFC.NS',
            'WIPRO.NS', 'KOTAK.NS', 'LT.NS', 'SBIN.NS', 'MARUTI.NS'
        ]

    def get_current_prices(self) -> Dict:
        """Fetch current prices for all stocks"""
        prices = {}

        logger.info(f"Fetching current prices for {len(self.stocks)} stocks...")
        print("\n" + "=" * 80)
        print("LIVE NSE MARKET PRICES")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(f"{'Stock Symbol':<20} {'Current Price':<20} {'Change (%)':<15} {'Status':<10}")
        print("-" * 80)

        for symbol in self.stocks:
            try:
                # Get latest data (1 day)
                data = yf.download(symbol, period='5d', progress=False)

                if data.empty or len(data) < 2:
                    print(f"{symbol:<20} {'N/A':<20} {'N/A':<15} {'No Data':<10}")
                    continue

                current_price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100

                status = "📈 UP" if change_pct > 0 else "📉 DOWN" if change_pct < 0 else "→ SAME"

                prices[symbol] = {
                    'current': current_price,
                    'previous': prev_close,
                    'change': change_pct,
                    'status': status
                }

                print(f"{symbol:<20} ₹{current_price:<18.2f} {change_pct:>7.2f}% {status:<10}")

            except Exception as e:
                logger.warning(f"Error fetching {symbol}: {e}")
                print(f"{symbol:<20} {'ERROR':<20} {'N/A':<15} {'Failed':<10}")

        print("-" * 80)
        print("=" * 80 + "\n")

        return prices

    def get_top_movers(self, prices: Dict, limit: int = 5) -> List:
        """Get top gainers and losers"""
        if not prices:
            return []

        sorted_stocks = sorted(prices.items(), key=lambda x: x[1]['change'], reverse=True)

        print("\n" + "=" * 80)
        print("TOP MOVERS")
        print("=" * 80)

        print("\n🚀 TOP GAINERS:")
        print("-" * 80)
        print(f"{'Stock':<20} {'Price':<20} {'Gain %':<15}")
        print("-" * 80)

        for symbol, data in sorted_stocks[:limit]:
            if data['change'] > 0:
                print(f"{symbol:<20} ₹{data['current']:<18.2f} +{data['change']:.2f}%")

        print("\n📉 TOP LOSERS:")
        print("-" * 80)
        print(f"{'Stock':<20} {'Price':<20} {'Loss %':<15}")
        print("-" * 80)

        for symbol, data in reversed(sorted_stocks[-limit:]):
            if data['change'] < 0:
                print(f"{symbol:<20} ₹{data['current']:<18.2f} {data['change']:.2f}%")

        print("=" * 80 + "\n")

        return sorted_stocks

    def display_detailed_info(self, symbol: str):
        """Display detailed info for a stock"""
        try:
            logger.info(f"Fetching detailed data for {symbol}...")
            data = yf.download(symbol, period='1mo', progress=False)

            if data.empty:
                print(f"No data available for {symbol}")
                return

            current = data['Close'].iloc[-1]
            open_price = data['Open'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            volume = data['Volume'].iloc[-1]

            print(f"\n{'=' * 60}")
            print(f"DETAILED INFO - {symbol}")
            print(f"{'=' * 60}")
            print(f"Current Price:     ₹{current:.2f}")
            print(f"Open:              ₹{open_price:.2f}")
            print(f"High (Today):      ₹{high:.2f}")
            print(f"Low (Today):       ₹{low:.2f}")
            print(f"Volume:            {volume:,.0f}")
            print(f"52-Week High:      ₹{data['High'].max():.2f}")
            print(f"52-Week Low:       ₹{data['High'].min():.2f}")
            print(f"Timestamp:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 60}\n")

        except Exception as e:
            logger.error(f"Error fetching detailed info for {symbol}: {e}")


def main():
    market = MarketPrices()

    # Get current prices
    prices = market.get_current_prices()

    # Show top movers
    if prices:
        market.get_top_movers(prices)

        # Example: Get detailed info for top gainer
        if prices:
            top_stock = sorted(prices.items(), key=lambda x: x[1]['change'], reverse=True)[0]
            market.display_detailed_info(top_stock[0])


if __name__ == "__main__":
    main()
