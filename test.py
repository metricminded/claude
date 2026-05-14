#!/usr/bin/env python3
"""
Quick test script to verify setup
"""

import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all required packages are installed"""
    logger.info("Testing imports...")
    try:
        import yfinance
        import pandas
        import numpy
        import schedule
        logger.info("✓ All packages imported successfully")
        return True
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        logger.error("Run: pip install -r requirements.txt")
        return False

def test_config():
    """Test config file exists and is valid"""
    logger.info("Testing config file...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Check required fields
        required = ['email', 'scheduler', 'analysis']
        for field in required:
            if field not in config:
                logger.error(f"✗ Missing '{field}' in config.json")
                return False

        # Check email fields
        if 'recipient' not in config['email']:
            logger.error("✗ Missing 'email.recipient' in config.json")
            return False
        if 'your-email' in config['email']['recipient']:
            logger.error("✗ Email not configured - update config.json")
            return False

        logger.info("✓ Config file valid")
        return True
    except FileNotFoundError:
        logger.error("✗ config.json not found")
        logger.error("Run: cp config.json.template config.json")
        return False
    except json.JSONDecodeError:
        logger.error("✗ config.json is not valid JSON")
        return False

def test_analyzer():
    """Test stock analyzer with 5 stocks"""
    logger.info("Testing stock analyzer (may take 30-60 seconds)...")
    try:
        from stock_analyzer import StockAnalyzer

        analyzer = StockAnalyzer()
        # Test with just 5 stocks for speed
        analyzer.nse_stocks = analyzer.nse_stocks[:5]

        stocks = analyzer.get_top_stocks(limit=2)

        if not stocks:
            logger.error("✗ Analyzer returned no results")
            return False

        logger.info(f"✓ Analyzer working - found {len(stocks)} stocks")
        for stock in stocks:
            logger.info(f"  - {stock['symbol']}: Score {stock['score']}/7")
        return True
    except Exception as e:
        logger.error(f"✗ Analyzer error: {e}")
        return False

def main():
    logger.info("=" * 60)
    logger.info("Stock Analyzer Setup Test")
    logger.info("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Config", test_config),
        ("Analyzer", test_analyzer),
    ]

    results = []
    for name, test_func in tests:
        logger.info(f"\n[{name}]")
        result = test_func()
        results.append((name, result))

    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
        if not result:
            all_passed = False

    if all_passed:
        logger.info("\n✓ All tests passed!")
        logger.info("\nNext steps:")
        logger.info("1. Verify config.json settings")
        logger.info("2. Run: python scheduler.py")
        return 0
    else:
        logger.error("\n✗ Some tests failed - fix issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
