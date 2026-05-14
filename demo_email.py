#!/usr/bin/env python3
"""
Demo: Generate and send sample stock alert email
Shows the complete workflow
"""

import logging
from stock_analyzer_demo import get_demo_stocks
from notifier import EmailNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("DEMO: Generating Stock Alert Email")
    logger.info("=" * 60)

    # Get demo stocks
    stocks = get_demo_stocks()
    logger.info(f"\n✓ Generated {len(stocks)} demo stocks")

    # Create notifier and prepare email
    notifier = EmailNotifier("your-email@example.com")

    logger.info("\n📧 Preparing email...")
    if notifier.send_stock_alert(stocks):
        logger.info("✓ Email prepared successfully!")

        logger.info("\n" + "=" * 60)
        logger.info("EMAIL READY TO SEND")
        logger.info("=" * 60)
        logger.info("\nCheck these files:")
        logger.info("  • stock_alert_*.html - Email content")
        logger.info("  • email_to_send.json - Email data for Gmail MCP")
        logger.info("  • email_metadata.json - Metadata")

        logger.info("\nTo send via Gmail MCP:")
        logger.info("  1. Run: python send_email.py")
        logger.info("  2. Use email_to_send.json with create_draft tool")
        logger.info("\n" + "=" * 60)
    else:
        logger.error("✗ Failed to prepare email")


if __name__ == "__main__":
    main()
