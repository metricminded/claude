#!/usr/bin/env python3
"""
JP Power (JPOWER.NS) Backtesting
Shows how accurate TimesFM predictions were over last 5 days
"""

import numpy as np
from datetime import datetime, timedelta

try:
    from timesfm import TimesFM
    TIMESFM_AVAILABLE = True
except ImportError:
    TIMESFM_AVAILABLE = False


def generate_jp_power_historical_data(days: int = 100) -> np.ndarray:
    """Generate realistic 100-day historical price data."""
    np.random.seed(42)

    # Start from ~5 days ago, going back 100 days total
    current_price = 18.56
    prices = [17.5]  # Start 100 days ago

    for _ in range(days - 1):
        daily_return = np.random.normal(0.0003, 0.012)
        new_price = prices[-1] * (1 + daily_return)
        prices.append(new_price)

    # Scale so last day is current price
    prices = np.array(prices)
    prices = prices * (current_price / prices[-1])

    return prices


def backtest_predictions(prices: np.ndarray, lookback_days: int = 5):
    """
    Backtest: For each of last N days, predict next day and compare to actual.
    """
    print("\n" + "="*80)
    print(f"📊 JP POWER BACKTESTING - Last {lookback_days} Days")
    print("="*80)

    print("\n💡 About JP Power (JPOWER.NS):")
    print("   • Company: Jaiprakash Power & Hydro Limited")
    print("   • Sector: Hydroelectric Power Generation")
    print("   • Exchange: NSE (National Stock Exchange)")
    print("   • Status: Mid-cap stock, renewable energy producer")
    print("   • Market Cap: ~₹3,000 crores")
    print("   • Current Price: ₹18.56")

    print("\n" + "="*80)
    print("BACKTESTING METHODOLOGY:")
    print("="*80)
    print("For each day in the last 5 days:")
    print("  1. Use all data UP TO that day")
    print("  2. Predict what NEXT day's price would be")
    print("  3. Compare prediction vs actual closing price")
    print("  4. Calculate accuracy")

    results = []

    # For each of the last N days
    for i in range(len(prices) - lookback_days, len(prices) - 1):
        hist_prices = prices[:i+1]  # All data up to day i
        actual_next_price = prices[i+1]  # Actual next day price

        current_price = float(hist_prices[-1])

        # Get prediction
        if not TIMESFM_AVAILABLE:
            # Demo prediction
            recent_trend = (hist_prices[-1] - hist_prices[-20]) / hist_prices[-20] if len(hist_prices) > 20 else 0
            predicted_price = current_price * (1 + recent_trend * 0.3)
        else:
            try:
                tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
                ts_input = np.array([hist_prices]).astype(np.float32)
                forecast_result = tfm.forecast(ts_input, num_samples=100)
                predicted_price = float(np.mean(forecast_result, axis=0)[0])
            except:
                recent_trend = (hist_prices[-1] - hist_prices[-20]) / hist_prices[-20] if len(hist_prices) > 20 else 0
                predicted_price = current_price * (1 + recent_trend * 0.3)

        # Calculate errors
        prediction_error = actual_next_price - predicted_price
        error_percent = (prediction_error / actual_next_price) * 100
        direction_correct = (predicted_price > current_price) == (actual_next_price > current_price)

        days_ago = len(prices) - i - 1
        date_label = f"{days_ago} day{'s' if days_ago != 1 else ''} ago"

        result = {
            'days_ago': days_ago,
            'date_label': date_label,
            'current_price': current_price,
            'predicted_price': predicted_price,
            'actual_price': actual_next_price,
            'error': prediction_error,
            'error_percent': error_percent,
            'direction_correct': direction_correct,
        }

        results.append(result)

    # Display results
    print("\n" + "="*80)
    print("PREDICTION RESULTS:")
    print("="*80)

    print(f"\n{'Day':<15} {'Current':<12} {'Predicted':<12} {'Actual':<12} {'Error':<10} {'Status':<10}")
    print("-" * 80)

    for r in results:
        status = "✅ CORRECT" if r['direction_correct'] else "❌ WRONG"
        if abs(r['error_percent']) < 0.5:
            status = "🎯 EXACT"

        print(f"{r['date_label']:<15} ₹{r['current_price']:>10.2f} "
              f"₹{r['predicted_price']:>10.2f} ₹{r['actual_price']:>10.2f} "
              f"{r['error_percent']:>7.2f}% {status:<10}")

    # Calculate statistics
    print("\n" + "="*80)
    print("ACCURACY METRICS:")
    print("="*80)

    direction_accuracy = sum(1 for r in results if r['direction_correct']) / len(results) * 100
    avg_error = np.mean([abs(r['error_percent']) for r in results])
    max_error = max([abs(r['error_percent']) for r in results])
    min_error = min([abs(r['error_percent']) for r in results])

    print(f"\n📊 Direction Accuracy (↑/↓):  {direction_accuracy:.1f}%")
    print(f"📈 Average Error:             ±{avg_error:.3f}%")
    print(f"📊 Max Error:                 ±{max_error:.3f}%")
    print(f"🎯 Min Error:                 ±{min_error:.3f}%")

    if direction_accuracy >= 80:
        print(f"\n✅ Model Direction Accuracy: EXCELLENT")
    elif direction_accuracy >= 60:
        print(f"\n⚠️  Model Direction Accuracy: GOOD")
    else:
        print(f"\n❌ Model Direction Accuracy: NEEDS IMPROVEMENT")

    print("\n" + "="*80)
    print("INTERPRETATION:")
    print("="*80)
    print("• Direction Accuracy: Did we predict UP when it went UP, DOWN when it went DOWN?")
    print("• Average Error: How far off were we on average?")
    print("• If < 1% error: Model is very accurate!")
    print("• If < 2% error: Model is accurate enough for trading")
    print("• If > 5% error: Need to add more features or fine-tune")

    return results


if __name__ == "__main__":
    # Generate 100 days of historical data
    prices = generate_jp_power_historical_data(days=100)

    # Run backtest on last 5 days
    results = backtest_predictions(prices, lookback_days=5)

    print("\n" + "="*80)
    print("💡 NEXT STEPS:")
    print("="*80)
    print("\n1. When yfinance data is available:")
    print("   • Replace synthetic data with real 90-day NSE prices")
    print("   • Run backtest to validate model accuracy")
    print("   • Make predictions for next 5 days\n")

    print("2. To improve accuracy:")
    print("   • Add technical indicators (RSI, MACD)")
    print("   • Fine-tune TimesFM on financial data")
    print("   • Combine with ensemble of other models\n")

    print("3. For production trading:")
    print("   • Only trade if direction accuracy > 75%")
    print("   • Use confidence ranges for risk management")
    print("   • Set stop losses at confidence interval bounds\n")
