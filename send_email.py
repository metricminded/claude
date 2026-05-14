#!/usr/bin/env python3
"""
Send email via Gmail MCP connector
Call this from Claude Code or manually after analyzer runs
"""

import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_stock_email_content():
    """Read the latest stock alert"""
    try:
        with open("email_metadata.json", "r") as f:
            metadata = json.load(f)

        with open(metadata["html_file"], "r") as f:
            html_content = f.read()

        return {
            "subject": metadata["subject"],
            "recipient": metadata["recipient"],
            "html": html_content,
        }
    except FileNotFoundError:
        logger.error("No email prepared. Run stock analyzer first.")
        return None


def send_via_gmail_mcp(email_data):
    """
    Instructions for sending via Gmail MCP tool:

    In Claude Code, call:
    mcp__662aa3ce-db69-4cf6-889c-980e4d49e9bb__create_draft

    With parameters:
    - to: [email_data["recipient"]]
    - subject: email_data["subject"]
    - htmlBody: email_data["html"]
    """
    if not email_data:
        return False

    print("\n" + "=" * 60)
    print("SEND EMAIL VIA GMAIL MCP CONNECTOR")
    print("=" * 60)
    print(f"\nSubject: {email_data['subject']}")
    print(f"To: {email_data['recipient']}")
    print(f"\nContent preview: {email_data['html'][:200]}...")

    print("\n" + "=" * 60)
    print("HOW TO SEND:")
    print("=" * 60)
    print("\n1. Open Claude Code")
    print("2. Run this command:")
    print("")
    print("   python send_email.py --send")
    print("")
    print("3. Or manually use Gmail MCP tool with:")
    print(f"   To: {email_data['recipient']}")
    print(f"   Subject: {email_data['subject']}")
    print(f"   Body: <HTML content from {email_data['recipient']}...>")

    print("\n" + "=" * 60)

    # Save for easy copying
    with open("email_to_send.json", "w") as f:
        json.dump({
            "to": [email_data["recipient"]],
            "subject": email_data["subject"],
            "htmlBody": email_data["html"]
        }, f, indent=2)

    print("✓ Email data saved to: email_to_send.json")
    print("  You can use this in Gmail MCP create_draft tool")

    return True


if __name__ == "__main__":
    import sys

    email_data = get_stock_email_content()

    if email_data:
        send_via_gmail_mcp(email_data)

        if "--send" in sys.argv:
            print("\nTo send via Gmail MCP connector, use Claude Code:")
            print("1. Copy the email_to_send.json content")
            print("2. Call create_draft with that data")
    else:
        print("No email prepared yet. Run the stock analyzer first.")
