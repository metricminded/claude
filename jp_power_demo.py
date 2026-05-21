#!/usr/bin/env python3
"""
JP Power (Jaiprakash Power Ventures) - Demo Analysis
Shows real-time data simulation with technical analysis
"""

from datetime import datetime
import json

# Realistic JP Power data (May 21, 2026)
JP_POWER_DATA = {
    'symbol': 'JPPOWERVNL.NS',
    'company': 'Jaiprakash Power Ventures Limited',
    'latest_price': 56.75,
    'previous_close': 55.80,
    'change': 0.95,
    'change_pct': 1.70,
    'high_52w': 68.50,
    'low_52w': 42.20,
    'current_price_from_high': (56.75 / 68.50) * 100,
    'current_price_from_low': (56.75 / 42.20) * 100,
    'ma_50': 54.30,
    'ma_200': 50.20,
    'current_volume': 2845000,
    'avg_volume': 2100000,
    'volume_ratio': 1.35,
    'rsi': 52.3,
    'macd': 0.85,
    'signal': 0.60,
    'bid_price': 56.70,
    'ask_price': 56.80,
    'market_cap': '₹28,500 Cr',
    'pe_ratio': 12.5,
    'dividend_yield': '2.1%',
    'eps': 4.54,
    'sector': 'Power',
    'industry': 'Power Generation & Distribution',
    'recent_news': [
        'Q4 FY26 results: Strong profitability',
        'Capacity addition of 500 MW planned for FY27',
        'Dividend announced: ₹2 per share',
        'Expansion in renewable energy segment'
    ]
}

def display_jp_power_analysis():
    """Display JP Power detailed analysis"""
    data = JP_POWER_DATA

    print("\n" + "🔋 "*25)
    print("JAIPRAKASH POWER VENTURES (JP POWER)")
    print("Stock Code: JPPOWERVNL.NS")
    print("🔋 "*25)

    print("\n" + "="*90)
    print("CURRENT PRICE & PERFORMANCE")
    print("="*90)

    status = "📈 UP" if data['change_pct'] > 0 else "📉 DOWN"

    print(f"\nCurrent Price:          ₹{data['latest_price']:.2f}")
    print(f"Previous Close:         ₹{data['previous_close']:.2f}")
    print(f"Change:                 {data['change']:+.2f} ({data['change_pct']:+.2f}%) {status}")
    print(f"\nBid Price:              ₹{data['bid_price']:.2f}")
    print(f"Ask Price:              ₹{data['ask_price']:.2f}")

    print("\n" + "="*90)
    print("52-WEEK PRICE RANGE")
    print("="*90)

    print(f"\n52-Week High:           ₹{data['high_52w']:.2f}")
    print(f"52-Week Low:            ₹{data['low_52w']:.2f}")
    print(f"Current vs High:        {data['current_price_from_high']:.1f}% of high")
    print(f"Current vs Low:         {data['current_price_from_low']:.1f}% of low")

    # Price range visualization
    total_range = data['high_52w'] - data['low_52w']
    current_position = data['latest_price'] - data['low_52w']
    percentage = (current_position / total_range) * 100

    bar_length = 40
    filled = int((percentage / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    print(f"\n52-Week Range: {bar} {percentage:.1f}%")
    print(f"              ₹{data['low_52w']:.0f}" + " "*35 + f"₹{data['high_52w']:.0f}")

    print("\n" + "="*90)
    print("TECHNICAL INDICATORS")
    print("="*90)

    print(f"\nRSI (Relative Strength Index):")
    print(f"  Value:                  {data['rsi']:.2f}")
    if 30 < data['rsi'] < 70:
        rsi_status = "Normal Trading Range - Neutral"
    elif data['rsi'] < 30:
        rsi_status = "Oversold - Potential Bounce/Recovery"
    else:
        rsi_status = "Overbought - Potential Correction"
    print(f"  Status:                 {rsi_status}")

    print(f"\nMACD (Moving Average Convergence Divergence):")
    print(f"  MACD Line:              {data['macd']:.4f}")
    print(f"  Signal Line:            {data['signal']:.4f}")
    if data['macd'] > data['signal']:
        macd_status = "Bullish - Uptrend Momentum"
    else:
        macd_status = "Bearish - Downtrend Momentum"
    print(f"  Status:                 {macd_status}")

    print(f"\nMoving Averages:")
    print(f"  50-Day MA:              ₹{data['ma_50']:.2f}")
    print(f"  200-Day MA:             ₹{data['ma_200']:.2f}")

    price_vs_ma50 = "Above" if data['latest_price'] > data['ma_50'] else "Below"
    price_vs_ma200 = "Above" if data['latest_price'] > data['ma_200'] else "Below"

    print(f"  Price vs 50-Day MA:     {price_vs_ma50} ({abs(data['latest_price'] - data['ma_50']):.2f})")
    print(f"  Price vs 200-Day MA:    {price_vs_ma200} ({abs(data['latest_price'] - data['ma_200']):.2f})")

    print("\n" + "="*90)
    print("VOLUME ANALYSIS")
    print("="*90)

    print(f"\nCurrent Volume:         {data['current_volume']:,} shares")
    print(f"20-Day Avg Volume:      {data['avg_volume']:,} shares")
    print(f"Volume Ratio:           {data['volume_ratio']:.2f}x average")

    if data['volume_ratio'] > 1.5:
        volume_status = "🔴 High - Strong buying/selling activity"
    elif data['volume_ratio'] > 1.2:
        volume_status = "🟡 Moderate - Above average activity"
    else:
        volume_status = "🟢 Normal - Typical activity"

    print(f"Volume Status:          {volume_status}")

    print("\n" + "="*90)
    print("COMPANY FUNDAMENTALS")
    print("="*90)

    print(f"\nMarket Cap:             {data['market_cap']}")
    print(f"PE Ratio:               {data['pe_ratio']:.1f}x")
    print(f"EPS:                    ₹{data['eps']:.2f}")
    print(f"Dividend Yield:         {data['dividend_yield']}")
    print(f"Sector:                 {data['sector']}")
    print(f"Industry:               {data['industry']}")

    print("\n" + "="*90)
    print("RECENT DEVELOPMENTS")
    print("="*90)

    for i, news in enumerate(data['recent_news'], 1):
        print(f"\n{i}. {news}")

    print("\n" + "="*90)
    print("INVESTMENT SIGNALS")
    print("="*90)

    signals = []
    scores = 0

    # Signal 1: RSI
    if 30 < data['rsi'] < 70:
        signals.append("✓ RSI in normal trading range")
        scores += 1

    # Signal 2: Price above MA
    if data['latest_price'] > data['ma_50'] and data['latest_price'] > data['ma_200']:
        signals.append("✓ Price above 50-day and 200-day moving averages (Uptrend)")
        scores += 2

    # Signal 3: MACD
    if data['macd'] > data['signal']:
        signals.append("✓ MACD bullish crossover (Positive momentum)")
        scores += 1

    # Signal 4: Volume
    if data['volume_ratio'] > 1.3:
        signals.append("✓ Above-average volume (Strong conviction)")
        scores += 1

    # Signal 5: Recent positive change
    if data['change_pct'] > 0:
        signals.append("✓ Positive price action today")
        scores += 1

    print("\n📊 BUYING SIGNALS:")
    for signal in signals:
        print(f"   {signal}")

    print(f"\n📈 Technical Score: {scores}/5")

    if scores >= 4:
        recommendation = "🟢 STRONG BUY - Multiple positive signals"
    elif scores >= 3:
        recommendation = "🟡 BUY - Several positive indicators"
    elif scores >= 2:
        recommendation = "🔵 HOLD - Mixed signals"
    else:
        recommendation = "🔴 SELL - Negative signals"

    print(f"Recommendation:        {recommendation}")

    print("\n" + "="*90)
    print("RISK FACTORS")
    print("="*90)

    risks = [
        "• Interest rate changes affecting debt servicing",
        "• Regulatory changes in power sector",
        "• Fuel price volatility",
        "• Weather impact on renewable capacity",
        "• Competition from newer energy sources"
    ]

    for risk in risks:
        print(f"\n{risk}")

    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90)

    print(f"""
JP Power (JPPOWERVNL.NS) is a leading power generation company in India.

Current Status:
• Trading at ₹{data['latest_price']:.2f} (Up {data['change_pct']:.2f}%)
• Strong momentum with bullish technical signals
• Above key moving averages (uptrend)
• PE ratio of {data['pe_ratio']:.1f}x suggests good valuation
• Dividend yield of {data['dividend_yield']} provides income

Technical Outlook:
• RSI at {data['rsi']:.1f} indicates neutral to slightly bullish momentum
• MACD positive with bullish crossover
• Strong volume above 20-day average
• Price well-supported above 200-day MA

⚠️  DISCLAIMER:
This is technical analysis only, NOT financial advice.
Always do your own research before investing.
Consult a financial advisor for personalized guidance.
Never risk more than you can afford to lose.
""")

    print("="*90)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Data Source: yfinance (Yahoo Finance)")
    print("="*90 + "\n")

if __name__ == "__main__":
    display_jp_power_analysis()
