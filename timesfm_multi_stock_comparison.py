#!/usr/bin/env python3
"""Compare TimesFM predictions across multiple stocks."""

import numpy as np
from datetime import datetime

try:
    from timesfm import TimesFM
    TIMESFM_AVAILABLE = True
except ImportError:
    TIMESFM_AVAILABLE = False


def generate_stock_prices(symbol: str, days: int = 90) -> np.ndarray:
    """Generate realistic synthetic prices for different stocks."""
    np.random.seed(hash(symbol) % 2**32)

    base_prices = {
        "RELIANCE.NS": 2450,    # Large cap - oil & gas
        "TCS.NS": 3600,         # Large cap - IT
        "JPOWER.NS": 180,       # Mid cap - Power/Hydro
        "SUNPHARMA.NS": 750,    # Large cap - Pharma
        "TITAN.NS": 3200,       # Large cap - Retail
    }

    current_price = base_prices.get(symbol, 2000)
    prices = [current_price]

    for _ in range(days - 1):
        daily_return = np.random.normal(0.0005, 0.015)
        new_price = prices[-1] * (1 + daily_return)
        prices.append(new_price)

    return np.array(prices)


def predict_stock(symbol: str) -> dict:
    """Get TimesFM prediction for a stock."""
    prices = generate_stock_prices(symbol, days=90)
    current_price = float(prices[-1])

    if not TIMESFM_AVAILABLE:
        # Demo prediction
        recent_trend = (prices[-1] - prices[-20]) / prices[-20]
        predicted_price = current_price * (1 + recent_trend * 0.3)
        change_percent = ((predicted_price - current_price) / current_price) * 100

        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "change_percent": change_percent,
            "mode": "demo"
        }

    try:
        tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
        ts_input = np.array([prices]).astype(np.float32)
        forecast_result = tfm.forecast(ts_input, num_samples=100)

        predicted_price = float(np.mean(forecast_result, axis=0)[0])
        change_percent = ((predicted_price - current_price) / current_price) * 100

        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "change_percent": change_percent,
            "mode": "live"
        }

    except Exception as e:
        # Fallback to demo
        recent_trend = (prices[-1] - prices[-20]) / prices[-20]
        predicted_price = current_price * (1 + recent_trend * 0.3)
        change_percent = ((predicted_price - current_price) / current_price) * 100

        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "change_percent": change_percent,
            "mode": "demo"
        }


def main():
    stocks = ["RELIANCE.NS", "TCS.NS", "JPOWER.NS", "SUNPHARMA.NS", "TITAN.NS"]

    print("\n" + "="*80)
    print("📊 TimesFM MULTI-STOCK PRICE PREDICTIONS")
    print("="*80)

    predictions = []
    for stock in stocks:
        pred = predict_stock(stock)
        predictions.append(pred)

    # Sort by change percent (descending)
    predictions.sort(key=lambda x: x['change_percent'], reverse=True)

    # Display as table
    print(f"\n{'Stock':<15} {'Current':<12} {'Predicted':<12} {'Change':<12} {'Status':<10}")
    print("-" * 80)

    for pred in predictions:
        change = pred['change_percent']
        arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        mode = "🤖" if pred['mode'] == "live" else "📝"

        print(f"{pred['symbol']:<15} ₹{pred['current_price']:>10.2f} "
              f"₹{pred['predicted_price']:>10.2f} {change:>9.3f}% {mode} {arrow}")

    print("-" * 80)

    print("\n📌 Top Performers (Expected Upside):")
    for i, pred in enumerate(predictions[:3], 1):
        print(f"   {i}. {pred['symbol']}: {pred['change_percent']:+.3f}%")

    print("\n⚡ JP Power Analysis:")
    jp_pred = next((p for p in predictions if p['symbol'] == 'JPOWER.NS'), None)
    if jp_pred:
        print(f"   • Current: ₹{jp_pred['current_price']:.2f}")
        print(f"   • Predicted: ₹{jp_pred['predicted_price']:.2f}")
        print(f"   • Expected Change: {jp_pred['change_percent']:+.3f}%")
        if jp_pred['change_percent'] > 0:
            print(f"   • Signal: BULLISH ✅")
        elif jp_pred['change_percent'] < -0.5:
            print(f"   • Signal: BEARISH ⚠️")
        else:
            print(f"   • Signal: NEUTRAL ➡️")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
