#!/usr/bin/env python3
"""
Intraday Trading Stock Analyzer
Identifies top 3 stocks to buy each morning based on technical analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from timesfm import TimesFM
    TIMESFM_AVAILABLE = True
except ImportError:
    TIMESFM_AVAILABLE = False
    logger.warning("TimesFM not installed. Install with: pip install timesfm")


class StockAnalyzer:
    def __init__(self):
        self.nse_stocks = self._get_top_nse_stocks(500)

    def _get_top_nse_stocks(self, count: int = 500) -> List[str]:
        """Get top NSE stocks by market cap/volume"""
        # Top liquid NSE stocks - you can customize this list
        top_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'INFOSY.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'HDFC.NS', 'WIPRO.NS', 'KOTAK.NS', 'LT.NS', 'BAJAJ-AUTO.NS',
            'MARUTI.NS', 'SUNPHARMA.NS', 'ASIANPAINT.NS', 'HCLTECH.NS', 'SBIN.NS',
            'BHARTIARTL.NS', 'ITC.NS', 'JSWSTEEL.NS', 'ULTRACEMCO.NS', 'BPCL.NS',
            'TATASTEEL.NS', 'ONGC.NS', 'EICHERMOT.NS', 'TITAN.NS', 'M&M.NS',
            'NESTLEIND.NS', 'POWERGRID.NS', 'HAVELLS.NS', 'DMART.NS', 'BOSCHIND.NS',
            'JPOWER.NS',  # JP Power - Hydro power producer
        ]
        return top_stocks[:count]

    def _calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, data: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD"""
        ema_12 = data.ewm(span=12).mean()
        ema_26 = data.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        return macd, signal

    def _predict_with_timesfm(self, prices: np.ndarray) -> Optional[Dict]:
        """Predict next day price using TimesFM"""
        if not TIMESFM_AVAILABLE or len(prices) < 20:
            return None

        try:
            tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
            ts_input = np.array([prices]).astype(np.float32)
            forecast_result = tfm.forecast(ts_input, num_samples=100)

            predicted_price = float(np.mean(forecast_result, axis=0)[0])
            lower_bound = float(np.percentile(forecast_result, 5, axis=0)[0])
            upper_bound = float(np.percentile(forecast_result, 95, axis=0)[0])

            current_price = float(prices[-1])
            price_change = predicted_price - current_price
            change_percent = (price_change / current_price) * 100

            return {
                'predicted_price': predicted_price,
                'price_change': price_change,
                'change_percent': change_percent,
                'confidence_lower': lower_bound,
                'confidence_upper': upper_bound,
            }
        except Exception as e:
            logger.debug(f"TimesFM prediction failed: {e}")
            return None

    def analyze_stock(self, symbol: str) -> Dict:
        """Analyze single stock and return signals"""
        try:
            # Fetch 3 months of data for analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            data = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if len(data) < 30:
                return None

            close = data['Close']
            volume = data['Volume']

            # Calculate indicators
            rsi = self._calculate_rsi(close)
            macd, signal = self._calculate_macd(close)

            sma_50 = close.rolling(window=50).mean()
            sma_200 = close.rolling(window=200).mean()

            # Latest values
            latest_close = close.iloc[-1]
            latest_rsi = rsi.iloc[-1]
            latest_macd = macd.iloc[-1]
            latest_signal = signal.iloc[-1]
            latest_volume = volume.iloc[-1]
            avg_volume = volume.iloc[-20:].mean()

            prev_close = close.iloc[-2]
            gap_up = ((latest_close - prev_close) / prev_close) * 100

            # Scoring system
            score = 0
            signals = []

            # RSI signal (30-70 range ideal for trading)
            if 30 < latest_rsi < 70:
                score += 1
                signals.append(f"RSI in trading range ({latest_rsi:.1f})")
            elif latest_rsi < 30:
                score += 2
                signals.append(f"RSI oversold ({latest_rsi:.1f}) - potential bounce")

            # MACD crossover
            if latest_macd > latest_signal and macd.iloc[-2] <= signal.iloc[-2]:
                score += 2
                signals.append("MACD bullish crossover")

            # Moving average crossover
            if sma_50.iloc[-1] > sma_200.iloc[-1]:
                score += 1
                signals.append("Price above 200-day MA")

            # Volume spike
            if latest_volume > avg_volume * 1.5:
                score += 1
                signals.append(f"Volume spike ({latest_volume/avg_volume:.1f}x avg)")

            # Gap up
            if gap_up > 0.5:
                score += 1
                signals.append(f"Gap up {gap_up:.2f}%")

            # TimesFM prediction
            timesfm_prediction = self._predict_with_timesfm(close.values)

            result = {
                'symbol': symbol,
                'price': latest_close,
                'score': score,
                'rsi': latest_rsi,
                'macd_momentum': latest_macd - latest_signal,
                'signals': signals,
                'gap_up': gap_up,
                'volume_ratio': latest_volume / avg_volume,
            }

            if timesfm_prediction:
                result['timesfm'] = timesfm_prediction

            return result

        except Exception as e:
            logger.warning(f"Error analyzing {symbol}: {e}")
            return None

    def get_top_stocks(self, limit: int = 3) -> List[Dict]:
        """Get top N stocks by score"""
        results = []

        logger.info(f"Analyzing {len(self.nse_stocks)} stocks...")
        for symbol in self.nse_stocks:
            analysis = self.analyze_stock(symbol)
            if analysis:
                results.append(analysis)

        # Sort by score, then by RSI proximity to ideal range
        results.sort(key=lambda x: (x['score'], abs(x['rsi'] - 50)), reverse=True)

        logger.info(f"Found {len(results)} valid stocks")
        return results[:limit]


def main():
    analyzer = StockAnalyzer()
    top_stocks = analyzer.get_top_stocks(limit=3)

    if not top_stocks:
        logger.error("Could not analyze any stocks")
        return None

    logger.info("=" * 60)
    logger.info("TOP 3 STOCKS TO BUY TODAY")
    logger.info("=" * 60)

    for i, stock in enumerate(top_stocks, 1):
        logger.info(f"\n{i}. {stock['symbol']}")
        logger.info(f"   Price: ₹{stock['price']:.2f}")
        logger.info(f"   Score: {stock['score']}/7")
        logger.info(f"   RSI: {stock['rsi']:.1f}")

        if 'timesfm' in stock:
            pred = stock['timesfm']
            logger.info(f"   TimesFM Prediction: ₹{pred['predicted_price']:.2f} ({pred['change_percent']:+.2f}%)")
            logger.info(f"   Confidence Range: ₹{pred['confidence_lower']:.2f} - ₹{pred['confidence_upper']:.2f}")

        logger.info(f"   Signals:")
        for signal in stock['signals']:
            logger.info(f"     • {signal}")

    logger.info("\n" + "=" * 60)
    logger.info("Disclaimer: This is technical analysis only.")
    logger.info("Do your own research before trading.")
    logger.info("=" * 60)

    return top_stocks


if __name__ == "__main__":
    main()
