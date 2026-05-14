#!/usr/bin/env python3
"""
Email notification system for daily stock recommendations
Uses Gmail MCP connector for reliable delivery
"""

from typing import List, Dict
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class EmailNotifier:
    def __init__(self, recipient_email: str):
        """
        Initialize email notifier
        Args:
            recipient_email: Email to send alerts to
        """
        self.recipient_email = recipient_email

    def send_stock_alert(self, stocks: List[Dict]) -> bool:
        """
        Generate email content for stock alert
        Note: Actual sending is done via Gmail MCP tools
        """
        try:
            # Create HTML email
            html_content = self._create_html_content(stocks)

            # Save to file for manual sending via Gmail MCP tool
            filename = f"stock_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filename, 'w') as f:
                f.write(html_content)

            subject = f"📈 Top 3 Intraday Stocks - {datetime.now().strftime('%Y-%m-%d')}"

            logger.info(f"Email ready: {filename}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Recipient: {self.recipient_email}")
            logger.info("To send: Use 'python send_email.py' command")

            # Also save metadata for sending
            metadata = {
                "subject": subject,
                "recipient": self.recipient_email,
                "html_file": filename,
                "timestamp": datetime.now().isoformat()
            }

            with open("email_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Failed to prepare email: {e}")
            return False

    def _create_html_content(self, stocks: List[Dict]) -> str:
        """Create HTML email content"""
        stocks_html = ""

        for i, stock in enumerate(stocks, 1):
            signals_html = "".join([f"<li>{signal}</li>" for signal in stock['signals']])

            stocks_html += f"""
            <div style="background-color: #f0f8ff; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; border-radius: 5px;">
                <h3 style="color: #333; margin-top: 0;">#{i} {stock['symbol']}</h3>
                <p><strong>Price:</strong> ₹{stock['price']:.2f}</p>
                <p><strong>Technical Score:</strong> {stock['score']}/7</p>
                <p><strong>RSI:</strong> {stock['rsi']:.1f}</p>
                <p><strong>Gap Up:</strong> {stock['gap_up']:.2f}%</p>
                <p><strong>Volume Ratio:</strong> {stock['volume_ratio']:.2f}x average</p>
                <p><strong>Why to Buy:</strong></p>
                <ul style="margin: 5px 0;">
                    {signals_html}
                </ul>
            </div>
            """

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                    .content {{ max-width: 600px; margin: 20px auto; }}
                    .footer {{ background-color: #ecf0f1; padding: 15px; margin-top: 20px; border-radius: 5px; font-size: 12px; color: #7f8c8d; }}
                </style>
            </head>
            <body>
                <div class="content">
                    <div class="header">
                        <h1>📈 Top 3 Intraday Trading Stocks</h1>
                        <p>{datetime.now().strftime('%d %B %Y - %A')}</p>
                    </div>

                    {stocks_html}

                    <div class="footer">
                        <p><strong>⚠️ Disclaimer:</strong></p>
                        <ul>
                            <li>This is technical analysis only, not financial advice</li>
                            <li>Past performance does not guarantee future results</li>
                            <li>Always do your own research before trading</li>
                            <li>Risk management is crucial - never risk more than you can afford to lose</li>
                            <li>Intraday trading involves high risk</li>
                        </ul>
                        <p><em>Generated at {datetime.now().strftime('%H:%M:%S IST')}</em></p>
                    </div>
                </div>
            </body>
        </html>
        """

        return html


def send_alert(stocks: List[Dict], config_file: str = "config.json"):
    """Convenience function to send alert"""
    import json

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        notifier = EmailNotifier(
            sender_email=config['email']['sender'],
            sender_password=config['email']['password'],
            recipient_email=config['email']['recipient']
        )

        return notifier.send_stock_alert(stocks)

    except FileNotFoundError:
        logger.error(f"Config file {config_file} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending alert: {e}")
        return False
