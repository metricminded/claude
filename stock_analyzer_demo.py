#!/usr/bin/env python3
"""
Demo stock analyzer with mock data
Shows how the system works with sample stocks
"""

import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_demo_stocks() -> List[Dict]:
    """Return demo stocks for testing"""
    return [
        {
            'symbol': 'RELIANCE.NS',
            'price': 2456.50,
            'score': 6,
            'rsi': 42.3,
            'macd_momentum': 0.85,
            'signals': [
                'RSI in trading range (42.3)',
                'MACD bullish crossover',
                'Volume spike (2.3x avg)'
            ],
            'gap_up': 1.23,
            'volume_ratio': 2.3,
        },
        {
            'symbol': 'TCS.NS',
            'price': 3845.75,
            'score': 5,
            'rsi': 38.9,
            'macd_momentum': 0.62,
            'signals': [
                'RSI oversold (38.9) - potential bounce',
                'Price above 200-day MA',
                'Volume spike (1.8x avg)'
            ],
            'gap_up': 0.89,
            'volume_ratio': 1.8,
        },
        {
            'symbol': 'INFOSY.NS',
            'price': 1624.40,
            'score': 5,
            'rsi': 35.2,
            'macd_momentum': 0.45,
            'signals': [
                'RSI oversold (35.2) - potential bounce',
                'Gap up 0.65%',
                'Volume spike (1.5x avg)'
            ],
            'gap_up': 0.65,
            'volume_ratio': 1.5,
        }
    ]


def main():
    top_stocks = get_demo_stocks()

    logger.info("=" * 60)
    logger.info("TOP 3 STOCKS TO BUY TODAY (DEMO)")
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
    logger.info("Disclaimer: This is technical analysis only.")
    logger.info("Do your own research before trading.")
    logger.info("=" * 60)

    return top_stocks


if __name__ == "__main__":
    main()
