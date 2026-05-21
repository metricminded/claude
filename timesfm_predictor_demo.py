"""TimesFM price prediction demo for NSE stocks (with synthetic data)."""
import numpy as np
from datetime import datetime, timedelta


def predict_stock_price_with_timesfm(symbol: str, days_back: int = 90) -> dict:
    """
    Predict next day's stock price using TimesFM.

    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS')
        days_back: Number of historical days to use for prediction

    Returns:
        Dictionary with prediction results
    """
    try:
        # Generate realistic synthetic price data (simulating actual stock movement)
        print(f"\n📊 Generating {days_back} days of synthetic price data for {symbol}...")

        # Create realistic price movements
        np.random.seed(hash(symbol) % 2**32)  # Consistent results per symbol
        prices = generate_realistic_prices(symbol, days_back)

        if len(prices) < 10:
            return {"error": f"Insufficient data for {symbol} (need at least 10 days)"}

        print(f"✅ Got {len(prices)} days of price data")
        print(f"   Price range: ₹{prices.min():.2f} - ₹{prices.max():.2f}")

        # Import TimesFM
        try:
            from timesfm import TimesFM
        except ImportError:
            print("⚠️ TimesFM not fully available. Showing demo prediction...")
            return demo_prediction(symbol, prices)

        # Initialize TimesFM model
        print("🤖 Loading TimesFM model (this may take a moment)...")
        tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)

        # Prepare data for TimesFM
        ts_input = np.array([prices]).astype(np.float32)

        # Get forecast
        print("🔮 Running TimesFM prediction...")
        forecast_result = tfm.forecast(ts_input, num_samples=100)

        # Extract prediction
        predicted_price = float(np.mean(forecast_result, axis=0)[0])
        lower_bound = float(np.percentile(forecast_result, 5, axis=0)[0])
        upper_bound = float(np.percentile(forecast_result, 95, axis=0)[0])

        current_price = float(prices[-1])
        price_change = predicted_price - current_price
        change_percent = (price_change / current_price) * 100

        result = {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "price_change": price_change,
            "change_percent": change_percent,
            "confidence_interval_lower": lower_bound,
            "confidence_interval_upper": upper_bound,
            "historical_days": len(prices),
            "timestamp": datetime.now().isoformat(),
            "model": "TimesFM",
            "mode": "live"
        }

        return result

    except Exception as e:
        print(f"⚠️ TimesFM failed, using demo prediction instead...")
        return demo_prediction(symbol, prices)


def generate_realistic_prices(symbol: str, days: int) -> np.ndarray:
    """Generate realistic synthetic stock prices."""
    np.random.seed(hash(symbol) % 2**32)

    # Base prices for different stocks
    base_prices = {
        "RELIANCE.NS": 2450,
        "TCS.NS": 3600,
        "INFOSY.NS": 1850,
        "HDFC.NS": 2300,
        "BAJAJ.NS": 8500
    }

    current_price = base_prices.get(symbol, 2000)

    # Generate realistic price movement with trend and volatility
    prices = [current_price]
    for _ in range(days - 1):
        # Random walk with small drift
        daily_return = np.random.normal(0.0005, 0.015)  # 0.05% drift, 1.5% volatility
        new_price = prices[-1] * (1 + daily_return)
        prices.append(new_price)

    return np.array(prices)


def demo_prediction(symbol: str, prices: np.ndarray) -> dict:
    """Demo prediction when TimesFM is not available."""
    current_price = float(prices[-1])

    # Simple trend-based prediction
    recent_trend = (prices[-1] - prices[-20]) / prices[-20] if len(prices) > 20 else 0
    predicted_price = current_price * (1 + recent_trend * 0.3)  # 30% of recent trend

    price_change = predicted_price - current_price
    change_percent = (price_change / current_price) * 100

    result = {
        "symbol": symbol,
        "current_price": current_price,
        "predicted_price": predicted_price,
        "price_change": price_change,
        "change_percent": change_percent,
        "confidence_interval_lower": predicted_price * 0.98,
        "confidence_interval_upper": predicted_price * 1.02,
        "historical_days": len(prices),
        "timestamp": datetime.now().isoformat(),
        "model": "SimpleMovingAverage (demo)",
        "mode": "demo"
    }

    return result


def print_prediction(result: dict) -> None:
    """Pretty print prediction results."""
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    mode_label = " [DEMO MODE]" if result.get("mode") == "demo" else ""
    print("\n" + "="*60)
    print(f"🎯 {result['model']} PREDICTION: {result['symbol']}{mode_label}")
    print("="*60)
    print(f"Current Price:     ₹{result['current_price']:.2f}")
    print(f"Predicted Price:   ₹{result['predicted_price']:.2f}")
    print(f"Expected Change:   ₹{result['price_change']:+.2f} ({result['change_percent']:+.2f}%)")
    print(f"Confidence Range:  ₹{result['confidence_interval_lower']:.2f} - ₹{result['confidence_interval_upper']:.2f}")
    print(f"Data Points Used:  {result['historical_days']} days")
    print("="*60)


if __name__ == "__main__":
    # Test with different stocks
    stocks = ["RELIANCE.NS", "TCS.NS", "INFOSY.NS"]

    for stock in stocks:
        result = predict_stock_price_with_timesfm(stock, days_back=90)
        print_prediction(result)
        print()
