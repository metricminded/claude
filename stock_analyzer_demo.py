#!/usr/bin/env python3
"""
Demo Stock Analyzer with sample data
Tests the full pipeline without external network
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemoStockAnalyzer:
    def __init__(self):
        self.demo_stocks = {
            'RELIANCE.NS': {
                'prices': [2450, 2455, 2460, 2458, 2462, 2465, 2468, 2470, 2472, 2475],
                'volumes': [50000000, 45000000, 55000000, 48000000, 60000000, 52000000,
                           58000000, 51000000, 59000000, 55000000]
            },
            'TCS.NS': {
                'prices': [3840, 3845, 3850, 3848, 3852, 3855, 3858, 3860, 3862, 3865],
                'volumes': [8000000, 7500000, 9000000, 7800000, 9500000, 8200000,
                           9200000, 8100000, 9100000, 8500000]
            },
            'INFOSY.NS': {
                'prices': [1870, 1875, 1880, 1878, 1882, 1885, 1888, 1890, 1892, 1895],
                'volumes': [12000000, 11500000, 13000000, 11800000, 13500000, 12200000,
                           13200000, 12100000, 13100000, 12500000]
            },
            'ICICIBANK.NS': {
                'prices': [1020, 1025, 1030, 1028, 1032, 1035, 1038, 1040, 1042, 1045],
                'volumes': [18000000, 17500000, 19000000, 17800000, 19500000, 18200000,
                           19200000, 18100000, 19100000, 18500000]
            },
            'HDFC.NS': {
                'prices': [2680, 2685, 2690, 2688, 2692, 2695, 2698, 2700, 2702, 2705],
                'volumes': [3000000, 2900000, 3200000, 2950000, 3300000, 3050000,
                           3250000, 3100000, 3200000, 3150000]
            },
        }

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI from prices"""
        if len(prices) < period + 1:
            return 50

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: List[float]) -> tuple:
        """Calculate MACD"""
        prices_array = np.array(prices)
        ema_12 = pd.Series(prices).ewm(span=12).mean().values
        ema_26 = pd.Series(prices).ewm(span=26).mean().values

        macd = ema_12 - ema_26
        signal = pd.Series(macd).ewm(span=9).mean().values

        return macd[-1], signal[-1]

    def analyze_stock(self, symbol: str) -> Dict:
        """Analyze stock with demo data"""
        if symbol not in self.demo_stocks:
            return None

        data = self.demo_stocks[symbol]
        prices = data['prices']
        volumes = data['volumes']

        latest_price = prices[-1]
        prev_price = prices[-2]
        latest_volume = volumes[-1]
        avg_volume = np.mean(volumes[-5:])

        rsi = self._calculate_rsi(prices)
        macd, signal = self._calculate_macd(prices)

        gap_up = ((latest_price - prev_price) / prev_price) * 100

        # Scoring
        score = 0
        signals = []

        if 30 < rsi < 70:
            score += 1
            signals.append(f"RSI in trading range ({rsi:.1f})")
        elif rsi < 30:
            score += 2
            signals.append(f"RSI oversold ({rsi:.1f}) - potential bounce")
        elif rsi > 70:
            score += 1
            signals.append(f"RSI overbought ({rsi:.1f})")

        if macd > signal:
            score += 2
            signals.append("MACD bullish momentum")

        if latest_volume > avg_volume * 1.5:
            score += 1
            signals.append(f"Volume spike ({latest_volume/avg_volume:.1f}x avg)")

        if gap_up > 0.5:
            score += 1
            signals.append(f"Gap up {gap_up:.2f}%")

        return {
            'symbol': symbol,
            'price': latest_price,
            'score': score,
            'rsi': rsi,
            'macd_momentum': macd - signal,
            'signals': signals,
            'gap_up': gap_up,
            'volume_ratio': latest_volume / avg_volume,
        }

    def get_top_stocks(self, limit: int = 3) -> List[Dict]:
        """Get top stocks by score"""
        results = []

        logger.info(f"Analyzing {len(self.demo_stocks)} demo stocks...")
        for symbol in self.demo_stocks.keys():
            analysis = self.analyze_stock(symbol)
            if analysis:
                results.append(analysis)

        results.sort(key=lambda x: (x['score'], abs(x['rsi'] - 50)), reverse=True)

        logger.info(f"Found {len(results)} valid stocks")
        return results[:limit]


def main():
    analyzer = DemoStockAnalyzer()
    top_stocks = analyzer.get_top_stocks(limit=3)

    if not top_stocks:
        logger.error("Could not analyze any stocks")
        return None

    logger.info("=" * 60)
    logger.info("TOP 3 STOCKS TO BUY TODAY (DEMO DATA)")
    logger.info("=" * 60)

    for i, stock in enumerate(top_stocks, 1):
        logger.info(f"\n{i}. {stock['symbol']}")
        logger.info(f"   Price: ₹{stock['price']:.2f}")
        logger.info(f"   Score: {stock['score']}/7")
        logger.info(f"   RSI: {stock['rsi']:.1f}")
        logger.info(f"   Signals:")
        for signal in stock['signals']:
            logger.info(f"     • {signal}")

    logger.info("\n" + "=" * 60)
    logger.info("Disclaimer: This is demo data for testing only.")
    logger.info("Use real data with proper stock analysis.")
    logger.info("=" * 60)

    return top_stocks


if __name__ == "__main__":
    main()
