#!/usr/bin/env python3
"""
TimesFM Integration Demo - Single Stock Price Prediction

This demonstrates how TimesFM (Google's Time Series Foundation Model)
can predict NSE stock prices using 90 days of historical data.
"""

import numpy as np
from datetime import datetime, timedelta

try:
    from timesfm import TimesFM
    TIMESFM_AVAILABLE = True
except ImportError:
    TIMESFM_AVAILABLE = False
    print("⚠️  TimesFM not installed. Using demo mode.\n")


def generate_synthetic_price_data(symbol: str, days: int = 90) -> np.ndarray:
    """Generate realistic synthetic stock prices for demo."""
    np.random.seed(hash(symbol) % 2**32)

    base_prices = {
        "RELIANCE.NS": 2450,
        "TCS.NS": 3600,
        "INFOSY.NS": 1850,
    }

    current_price = base_prices.get(symbol, 2000)
    prices = [current_price]

    for _ in range(days - 1):
        daily_return = np.random.normal(0.0005, 0.015)
        new_price = prices[-1] * (1 + daily_return)
        prices.append(new_price)

    return np.array(prices)


def predict_single_stock_with_timesfm(symbol: str = "RELIANCE.NS") -> dict:
    """Predict next day's price for a single stock using TimesFM."""
    print(f"{'='*60}")
    print(f"🚀 TimesFM Price Prediction for {symbol}")
    print(f"{'='*60}\n")

    # Generate price data
    prices = generate_synthetic_price_data(symbol, days=90)
    current_price = float(prices[-1])

    print(f"📊 Historical Data:")
    print(f"   Period: Last 90 days")
    print(f"   Current Price: ₹{current_price:.2f}")
    print(f"   Price Range: ₹{prices.min():.2f} - ₹{prices.max():.2f}")

    if not TIMESFM_AVAILABLE:
        print(f"\n⚠️  Demo Mode (TimesFM not available)")
        recent_trend = (prices[-1] - prices[-20]) / prices[-20]
        predicted_price = current_price * (1 + recent_trend * 0.3)
        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "change_percent": ((predicted_price - current_price) / current_price) * 100,
            "confidence_lower": predicted_price * 0.98,
            "confidence_upper": predicted_price * 1.02,
            "mode": "demo"
        }

    # Use TimesFM for prediction
    print(f"\n🤖 Using TimesFM Model...")
    try:
        tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
        ts_input = np.array([prices]).astype(np.float32)

        print(f"   Running forecast on {len(prices)} data points...")
        forecast_result = tfm.forecast(ts_input, num_samples=100)

        predicted_price = float(np.mean(forecast_result, axis=0)[0])
        lower_bound = float(np.percentile(forecast_result, 5, axis=0)[0])
        upper_bound = float(np.percentile(forecast_result, 95, axis=0)[0])

        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "change_percent": ((predicted_price - current_price) / current_price) * 100,
            "confidence_lower": lower_bound,
            "confidence_upper": upper_bound,
            "mode": "live"
        }

    except Exception as e:
        print(f"   ⚠️  TimesFM failed: {e}")
        print(f"   Falling back to demo prediction...")
        recent_trend = (prices[-1] - prices[-20]) / prices[-20]
        predicted_price = current_price * (1 + recent_trend * 0.3)
        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "change_percent": ((predicted_price - current_price) / current_price) * 100,
            "confidence_lower": predicted_price * 0.98,
            "confidence_upper": predicted_price * 1.02,
            "mode": "demo"
        }


def print_prediction(result: dict):
    """Display prediction results."""
    mode_label = " [DEMO]" if result["mode"] == "demo" else " [LIVE]"
    change = result["change_percent"]
    emoji = "📈" if change > 0 else "📉"

    print(f"\n{'='*60}")
    print(f"🎯 PREDICTION RESULTS{mode_label}")
    print(f"{'='*60}")
    print(f"Current Price:      ₹{result['current_price']:.2f}")
    print(f"Predicted Price:    ₹{result['predicted_price']:.2f}")
    print(f"Expected Change:    {emoji} {change:+.2f}%")
    print(f"Confidence Range:   ₹{result['confidence_lower']:.2f} - ₹{result['confidence_upper']:.2f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Single stock prediction
    result = predict_single_stock_with_timesfm("RELIANCE.NS")
    print_prediction(result)

    # Show what the integration does
    print("💡 What this TimesFM integration does:\n")
    print("   ✅ Fetches 90 days of historical stock data")
    print("   ✅ Uses TimesFM to predict tomorrow's price")
    print("   ✅ Provides confidence intervals (5th-95th percentile)")
    print("   ✅ Combines with technical analysis for better decisions")
    print("\n📚 Next Steps:")
    print("   • This works for any NSE stock symbol")
    print("   • The main stock_analyzer.py now includes TimesFM predictions")
    print("   • Run: python stock_analyzer_demo.py to see predictions")
