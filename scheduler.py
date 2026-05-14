#!/usr/bin/env python3
"""
Daily scheduler for stock analysis
Runs stock analyzer at 9:00 AM IST and sends email alert
"""

import schedule
import time
import logging
from datetime import datetime
import json
from stock_analyzer import StockAnalyzer
from notifier import send_alert

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_daily_analysis():
    """Run stock analysis and prepare email"""
    logger.info("=" * 60)
    logger.info("Starting daily stock analysis...")
    logger.info("=" * 60)

    try:
        # Analyze stocks
        analyzer = StockAnalyzer()
        top_stocks = analyzer.get_top_stocks(limit=3)

        if not top_stocks:
            logger.error("Failed to analyze stocks")
            return

        # Log results
        logger.info("Top 3 stocks identified:")
        for i, stock in enumerate(top_stocks, 1):
            logger.info(f"{i}. {stock['symbol']} - Score: {stock['score']}/7")

        # Prepare email alert
        try:
            from notifier import EmailNotifier
            with open('config.json', 'r') as f:
                config = json.load(f)

            notifier = EmailNotifier(config['email']['recipient'])
            if notifier.send_stock_alert(top_stocks):
                logger.info("✓ Analysis complete - email prepared")
                logger.info(f"  Email saved for sending via Gmail MCP connector")
                logger.info(f"  Run 'python send_email.py' to send")
            else:
                logger.warning("✗ Failed to prepare email")

        except Exception as e:
            logger.error(f"Error preparing email: {e}")

    except Exception as e:
        logger.error(f"Error in daily analysis: {e}")


def schedule_daily():
    """Schedule daily execution at 9:00 AM IST"""
    # 9:00 AM IST = 3:30 AM UTC (during daylight saving, adjust as needed)
    schedule.every().day.at("09:00").do(run_daily_analysis)

    logger.info("Scheduler started - will run at 09:00 AM IST daily")

    # Keep scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        schedule_daily()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
