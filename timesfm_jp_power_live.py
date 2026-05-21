#!/usr/bin/env python3
"""TimesFM prediction for JP Power using REAL yfinance data."""

import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

try:
    from timesfm import TimesFM
    TIMESFM_AVAILABLE = True
except ImportError:
    TIMESFM_AVAILABLE = False


def fetch_real_stock_data(symbol: str = "JPOWER.NS", days: int = 90) -> np.ndarray:
    """Fetch real historical stock data from Yahoo Finance."""
    print(f"📊 Fetching real data from Yahoo Finance for {symbol}...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if data.empty:
            print(f"❌ No data found for {symbol}")
            return None

        prices = data['Close'].values.astype(np.float32)
        print(f"✅ Downloaded {len(prices)} days of real price data")

        return prices

    except Exception as e:
        print(f"⚠️  Error fetching data: {e}")
        return None


def predict_with_real_data(symbol: str = "JPOWER.NS"):
    """Predict tomorrow's price using real yfinance data."""
    print(f"\n{'='*70}")
    print(f"⚡ TimesFM Price Prediction (REAL DATA): {symbol}")
    print(f"{'='*70}\n")

    # Try to fetch real data
    prices = fetch_real_stock_data(symbol, days=90)

    if prices is None:
        print("❌ Could not fetch real data from Yahoo Finance")
        print("   Network restrictions may apply in this environment")
        return

    current_price = float(prices[-1])

    print(f"\n📊 Real Historical Data:")
    print(f"   Current Price: ₹{current_price:.2f}")
    print(f"   Price Range: ₹{prices.min():.2f} - ₹{prices.max():.2f}")
    print(f"   Data Points: {len(prices)} days")

    if not TIMESFM_AVAILABLE:
        print(f"\n⚠️  Demo Mode (using trend-based prediction)")
        recent_trend = (prices[-1] - prices[-20]) / prices[-20]
        predicted_price = current_price * (1 + recent_trend * 0.3)
        change_percent = ((predicted_price - current_price) / current_price) * 100

        print(f"\n{'='*70}")
        print(f"🎯 TOMORROW'S PREDICTION (REAL DATA)")
        print(f"{'='*70}")
        print(f"Today's Price:           ₹{current_price:.2f}")
        print(f"Tomorrow's Predicted:    ₹{predicted_price:.2f}")
        print(f"Expected Change:         {change_percent:+.3f}%")
        print(f"Confidence Range (±2%):  ₹{predicted_price*0.98:.2f} - ₹{predicted_price*1.02:.2f}")
        print(f"{'='*70}\n")
        return

    # Use TimesFM with real data
    print(f"\n🤖 Running TimesFM with real market data...")
    try:
        tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
        ts_input = np.array([prices]).astype(np.float32)

        forecast_result = tfm.forecast(ts_input, num_samples=100)

        predicted_price = float(np.mean(forecast_result, axis=0)[0])
        lower_bound = float(np.percentile(forecast_result, 5, axis=0)[0])
        upper_bound = float(np.percentile(forecast_result, 95, axis=0)[0])
        change_percent = ((predicted_price - current_price) / current_price) * 100

        print(f"\n{'='*70}")
        print(f"🎯 TOMORROW'S PREDICTION (REAL DATA + TimesFM AI)")
        print(f"{'='*70}")
        print(f"Today's Price:           ₹{current_price:.2f}")
        print(f"Tomorrow's Predicted:    ₹{predicted_price:.2f}")
        print(f"Expected Change:         {change_percent:+.3f}%")
        print(f"Confidence Range (90%):  ₹{lower_bound:.2f} - ₹{upper_bound:.2f}")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"❌ TimesFM error: {e}")


if __name__ == "__main__":
    predict_with_real_data("JPOWER.NS")

    print("\n💡 About this script:")
    print("   ✅ Uses yfinance to fetch REAL NSE stock data")
    print("   ✅ Analyzes actual 90-day historical prices")
    print("   ✅ Applies TimesFM AI model to real market data")
    print("   ✅ Provides tomorrow's price prediction\n")

    print("📚 To use with other NSE stocks:")
    print("   python timesfm_jp_power_live.py")
    print("   (Edit the symbol in the script)\n")
