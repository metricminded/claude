#!/usr/bin/env python3
"""
LIVE TRADING SYSTEM - Real Market Data
Runs daily trade analysis with real NSE stock data from yfinance
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/trading_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from timesfm import TimesFM
    TIMESFM_AVAILABLE = True
    logger.info("✅ TimesFM available")
except ImportError:
    TIMESFM_AVAILABLE = False
    logger.warning("⚠️ TimesFM not available - using fallback prediction")


class LiveTradingSystem:
    """Live trading system with real yfinance data."""

    def __init__(self, profit_target: float = 1000):
        self.profit_target = profit_target
        self.nse_stocks = [
            'JPOWER.NS', 'RELIANCE.NS', 'TCS.NS', 'INFOSY.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'HDFC.NS', 'WIPRO.NS', 'KOTAK.NS', 'LT.NS',
            'BAJAJ-AUTO.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'ASIANPAINT.NS',
            'HCLTECH.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'JSWSTEEL.NS',
            'ULTRACEMCO.NS', 'BPCL.NS', 'TATASTEEL.NS', 'ONGC.NS', 'TITAN.NS',
            'M&M.NS', 'NESTLEIND.NS', 'POWERGRID.NS', 'HAVELLS.NS', 'DMART.NS'
        ]
        self.results = []

    def fetch_stock_data(self, symbol: str, days: int = 90) -> dict:
        """Fetch real data from yfinance."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            logger.info(f"📥 Fetching {symbol}...")
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if data.empty:
                logger.warning(f"⚠️  No data for {symbol}")
                return None

            return {
                'symbol': symbol,
                'prices': data['Close'].values.astype(np.float32),
                'volumes': data['Volume'].values.astype(np.float32),
                'dates': data.index,
                'current_price': float(data['Close'].iloc[-1])
            }

        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {e}")
            return None

    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI."""
        if len(prices) < period + 1:
            return 50
        deltas = np.diff(prices)
        seed = deltas[-period-1:]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        return 100 - 100 / (1 + rs)

    def calculate_macd(self, prices: np.ndarray) -> tuple:
        """Calculate MACD."""
        exp1 = pd.Series(prices).ewm(span=12).mean().values
        exp2 = pd.Series(prices).ewm(span=26).mean().values
        macd = exp1 - exp2
        signal = pd.Series(macd).ewm(span=9).mean().values
        return macd[-1], signal[-1]

    def predict_next_day(self, prices: np.ndarray) -> float:
        """Predict next day using TimesFM or fallback."""
        if not TIMESFM_AVAILABLE or len(prices) < 20:
            # Fallback: trend-based
            recent_trend = (prices[-1] - prices[-20]) / prices[-20]
            return prices[-1] * (1 + recent_trend * 0.3)

        try:
            tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
            ts_input = np.array([prices]).astype(np.float32)
            forecast_result = tfm.forecast(ts_input, num_samples=100)
            return float(np.mean(forecast_result, axis=0)[0])
        except:
            recent_trend = (prices[-1] - prices[-20]) / prices[-20]
            return prices[-1] * (1 + recent_trend * 0.3)

    def generate_signal(self, data: dict) -> dict:
        """Generate trade signal."""
        prices = data['prices']
        volumes = data['volumes']
        current = data['current_price']

        # Calculate indicators
        rsi = self.calculate_rsi(prices)
        macd, signal = self.calculate_macd(prices)
        predicted = self.predict_next_day(prices)
        vol_ratio = volumes[-1] / np.mean(volumes[-20:])

        # Score the trade
        score = 0
        signals = []

        if predicted > current:
            score += 2
            signals.append(f"Bullish prediction")
        else:
            signals.append(f"Bearish prediction")

        if rsi < 30:
            score += 2
            signals.append(f"RSI oversold ({rsi:.1f})")
        elif 30 < rsi < 70:
            score += 1
            signals.append(f"RSI neutral ({rsi:.1f})")

        if macd > signal:
            score += 2
            signals.append(f"MACD bullish")

        if vol_ratio > 1.5:
            score += 2
            signals.append(f"Volume spike ({vol_ratio:.1f}x)")

        price_change = abs((predicted - current) / current) * 100
        if price_change > 1:
            score += 2
            signals.append(f"Strong prediction ({price_change:.2f}%)")

        # Calculate position sizing
        expected_move = abs(predicted - current)
        quantity = max(1, int(self.profit_target / expected_move)) if expected_move > 0 else 50

        return {
            'symbol': data['symbol'],
            'current_price': current,
            'predicted_price': predicted,
            'direction': 'UP' if predicted > current else 'DOWN',
            'score': score,
            'rsi': rsi,
            'macd': macd - signal,
            'volume_ratio': vol_ratio,
            'quantity': quantity,
            'investment': current * quantity,
            'stop_loss': current * 0.995,
            'target_price': predicted,
            'expected_profit': self.profit_target,
            'confidence': 'HIGH' if score >= 8 else 'MEDIUM' if score >= 6 else 'LOW',
            'signals': signals,
        }

    def run_analysis(self):
        """Run analysis on all stocks."""
        logger.info("\n" + "="*80)
        logger.info("🚀 LIVE TRADING SYSTEM - Running Analysis")
        logger.info("="*80)
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Analyzing {len(self.nse_stocks)} NSE stocks...")

        trades = []

        for symbol in self.nse_stocks:
            data = self.fetch_stock_data(symbol)
            if data is None:
                continue

            signal = self.generate_signal(data)
            trades.append(signal)
            self.results.append(signal)

        # Sort by score
        trades.sort(key=lambda x: x['score'], reverse=True)

        return trades

    def display_results(self, trades: list):
        """Display trading results."""
        logger.info("\n" + "="*80)
        logger.info("📊 TOP TRADING OPPORTUNITIES")
        logger.info("="*80)

        # Show top 10 trades
        for i, trade in enumerate(trades[:10], 1):
            logger.info(f"\n{i}. {trade['symbol']} (Score: {trade['score']}/10)")
            logger.info(f"   Current: ₹{trade['current_price']:.2f}")
            logger.info(f"   Target:  ₹{trade['predicted_price']:.2f} ({trade['direction']})")
            logger.info(f"   Qty:     {trade['quantity']} shares")
            logger.info(f"   Invest:  ₹{trade['investment']:,.0f}")
            logger.info(f"   Signals: {', '.join(trade['signals'][:3])}")
            logger.info(f"   Confidence: {trade['confidence']}")

        # Highlight best trade
        if trades:
            best = trades[0]
            logger.info("\n" + "="*80)
            logger.info("🏆 BEST TRADE TODAY")
            logger.info("="*80)
            logger.info(f"Stock: {best['symbol']}")
            logger.info(f"Score: {best['score']}/10")
            logger.info(f"Entry: ₹{best['current_price']:.2f}")
            logger.info(f"Target: ₹{best['predicted_price']:.2f}")
            logger.info(f"Stop Loss: ₹{best['stop_loss']:.2f}")
            logger.info(f"Profit Target: ₹{best['expected_profit']}")
            logger.info(f"Risk/Reward: 1:{int(best['expected_profit']/abs(best['current_price']-best['stop_loss']))}")

        logger.info("\n" + "="*80)

    def save_results(self, trades: list):
        """Save results to JSON."""
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_stocks_analyzed': len(self.results),
            'trades_with_signals': len(trades),
            'high_confidence_trades': len([t for t in trades if t['score'] >= 8]),
            'top_trades': trades[:5]
        }

        filename = f"results/trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path('results').mkdir(exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        logger.info(f"\n💾 Results saved to {filename}")

        return filename


def main():
    """Main entry point."""
    logger.info("="*80)
    logger.info("LIVE TRADING SYSTEM - Starting")
    logger.info("="*80)

    system = LiveTradingSystem(profit_target=1000)

    try:
        # Run analysis
        trades = system.run_analysis()

        # Display results
        system.display_results(trades)

        # Save results
        system.save_results(trades)

        logger.info("\n✅ Analysis completed successfully")

    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
