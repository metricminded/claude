"""TimesFM price prediction for NSE stocks."""
import numpy as np
import pandas as pd
import yfinance as yf
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
        # Download historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        print(f"\n📊 Downloading {days_back} days of data for {symbol}...")
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if data.empty:
            return {"error": f"No data found for {symbol}"}

        # Get closing prices
        prices = data['Close'].values.astype(np.float32)

        if len(prices) < 10:
            return {"error": f"Insufficient data for {symbol} (need at least 10 days)"}

        print(f"✅ Got {len(prices)} days of price data")
        print(f"   Price range: ₹{prices.min():.2f} - ₹{prices.max():.2f}")

        # Import TimesFM
        try:
            from timesfm import TimesFM
        except ImportError:
            print("⚠️ TimesFM not installed. Run: pip install timesfm")
            return {"error": "TimesFM library not available"}

        # Initialize TimesFM model
        print("🤖 Loading TimesFM model...")
        tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)

        # Prepare data for TimesFM (needs to be a list of numpy arrays)
        # TimesFM expects shape: (batch_size, sequence_length)
        ts_input = np.array([prices]).astype(np.float32)

        # Get forecast
        print("🔮 Running TimesFM prediction...")
        forecast_result = tfm.forecast(ts_input, num_samples=100)

        # Extract prediction
        # forecast_result contains samples, get mean
        predicted_price = float(np.mean(forecast_result, axis=0)[0])

        # Calculate confidence interval (using percentiles from samples)
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
            "model": "TimesFM"
        }

        return result

    except Exception as e:
        return {"error": str(e), "symbol": symbol}


def print_prediction(result: dict) -> None:
    """Pretty print prediction results."""
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("\n" + "="*60)
    print(f"🎯 TimesFM PRICE PREDICTION: {result['symbol']}")
    print("="*60)
    print(f"Current Price:     ₹{result['current_price']:.2f}")
    print(f"Predicted Price:   ₹{result['predicted_price']:.2f}")
    print(f"Expected Change:   ₹{result['price_change']:+.2f} ({result['change_percent']:+.2f}%)")
    print(f"Confidence Range:  ₹{result['confidence_interval_lower']:.2f} - ₹{result['confidence_interval_upper']:.2f}")
    print(f"Data Points Used:  {result['historical_days']} days")
    print("="*60)


if __name__ == "__main__":
    # Test with a single stock
    result = predict_stock_price_with_timesfm("RELIANCE.NS", days_back=90)
    print_prediction(result)
