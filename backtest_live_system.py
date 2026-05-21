#!/usr/bin/env python3
"""
BACKTEST FRAMEWORK for Live Trading System
Tests the same strategy used in live_trading_system.py on historical data
Supports: 1 week, 1 month, 3 months, 6 months, 1 year backtests
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import argparse

# Setup logging
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


class BacktestEngine:
    """Backtest engine for the live trading system strategy."""

    def __init__(self, profit_target: float = 1000, capital: float = 200000,
                 stop_loss_pct: float = 0.005, min_score: int = 5):
        self.profit_target = profit_target
        self.capital = capital
        self.starting_capital = capital
        self.stop_loss_pct = stop_loss_pct
        self.min_score = min_score
        self.trade_history = []

        self.nse_stocks = [
            'JPOWER.NS', 'RELIANCE.NS', 'TCS.NS', 'INFOSY.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'WIPRO.NS', 'KOTAK.NS', 'LT.NS', 'MARUTI.NS',
            'SUNPHARMA.NS', 'ASIANPAINT.NS', 'HCLTECH.NS', 'SBIN.NS',
            'BHARTIARTL.NS', 'ITC.NS', 'TITAN.NS', 'M&M.NS', 'NESTLEIND.NS',
        ]

    def fetch_historical_data(self, symbol: str, period: str = "1y") -> dict:
        """Fetch real historical data using yfinance."""
        try:
            logger.info(f"📥 Fetching {symbol} ({period})...")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)

            if data.empty:
                logger.warning(f"⚠️  No data for {symbol}")
                return None

            return {
                'symbol': symbol,
                'prices': data['Close'].values,
                'volumes': data['Volume'].values,
                'dates': data.index,
                'high': data['High'].values,
                'low': data['Low'].values,
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
        if len(prices) < 26:
            return 0, 0
        exp1 = pd.Series(prices).ewm(span=12).mean().values
        exp2 = pd.Series(prices).ewm(span=26).mean().values
        macd = exp1 - exp2
        signal = pd.Series(macd).ewm(span=9).mean().values
        return macd[-1], signal[-1]

    def predict_next_day(self, prices: np.ndarray) -> float:
        """Predict next day price using TimesFM or fallback."""
        if not TIMESFM_AVAILABLE or len(prices) < 20:
            recent_trend = (prices[-1] - prices[-20]) / prices[-20] if len(prices) >= 20 else 0
            momentum = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
            return prices[-1] * (1 + (recent_trend * 0.3 + momentum * 0.4))

        try:
            tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
            ts_input = np.array([prices.astype(np.float32)])
            forecast_result = tfm.forecast(ts_input, num_samples=100)
            return float(np.mean(forecast_result, axis=0)[0])
        except:
            recent_trend = (prices[-1] - prices[-20]) / prices[-20] if len(prices) >= 20 else 0
            return prices[-1] * (1 + recent_trend * 0.3)

    def score_trade(self, prices: np.ndarray, volumes: np.ndarray) -> dict:
        """Score a trade opportunity (same logic as live system)."""
        current_price = float(prices[-1])
        predicted = self.predict_next_day(prices)
        rsi = self.calculate_rsi(prices)
        macd, signal = self.calculate_macd(prices)
        vol_ratio = volumes[-1] / np.mean(volumes[-20:]) if len(volumes) >= 20 else 1.0

        score = 0
        if predicted > current_price:
            score += 2
        if rsi < 30:
            score += 2
        elif 30 < rsi < 70:
            score += 1
        if macd > signal:
            score += 2
        if vol_ratio > 1.5:
            score += 2
        price_change = abs((predicted - current_price) / current_price) * 100
        if price_change > 1:
            score += 2

        return {
            'current': current_price,
            'predicted': predicted,
            'direction': 'UP' if predicted > current_price else 'DOWN',
            'score': score,
            'rsi': rsi,
            'macd_diff': macd - signal,
            'volume_ratio': vol_ratio,
        }

    def simulate_trade(self, entry: float, predicted: float, next_day_high: float,
                      next_day_low: float, next_day_close: float, direction: str) -> dict:
        """Simulate trade execution with stop loss & target."""
        expected_move = abs(predicted - entry)
        quantity = max(1, int(self.profit_target / expected_move)) if expected_move > 0 else 50

        # Limit position size by capital
        max_qty = int(self.capital * 0.5 / entry)  # Max 50% of capital per trade
        quantity = min(quantity, max_qty)

        investment = entry * quantity

        if direction == 'UP':
            target = predicted
            stop_loss = entry * (1 - self.stop_loss_pct)

            # Check if target hit during the day (using high)
            if next_day_high >= target:
                pnl = (target - entry) * quantity
                outcome = 'TARGET HIT ✅'
            # Check if stop loss hit (using low)
            elif next_day_low <= stop_loss:
                pnl = (stop_loss - entry) * quantity
                outcome = 'STOP LOSS ❌'
            else:
                pnl = (next_day_close - entry) * quantity
                outcome = 'CLOSED EOD'
        else:  # DOWN (SHORT)
            target = predicted
            stop_loss = entry * (1 + self.stop_loss_pct)

            if next_day_low <= target:
                pnl = (entry - target) * quantity
                outcome = 'TARGET HIT ✅'
            elif next_day_high >= stop_loss:
                pnl = (entry - stop_loss) * quantity
                outcome = 'STOP LOSS ❌'
            else:
                pnl = (entry - next_day_close) * quantity
                outcome = 'CLOSED EOD'

        return {
            'entry': entry,
            'target': target,
            'stop_loss': stop_loss,
            'quantity': quantity,
            'investment': investment,
            'pnl': pnl,
            'outcome': outcome,
            'direction': direction,
        }

    def run_backtest(self, period: str = "3mo", days_to_test: int = 60):
        """Run backtest on real historical data."""

        logger.info("\n" + "="*85)
        logger.info(f"📊 LIVE SYSTEM BACKTEST")
        logger.info("="*85)
        logger.info(f"Period: {period}")
        logger.info(f"Days to test: {days_to_test}")
        logger.info(f"Starting Capital: ₹{self.starting_capital:,.0f}")
        logger.info(f"Profit Target: ₹{self.profit_target}")
        logger.info(f"Stop Loss: {self.stop_loss_pct*100}%")
        logger.info(f"Min Score: {self.min_score}/10")
        logger.info(f"Stocks: {len(self.nse_stocks)}")

        # Fetch data for all stocks
        all_data = {}
        for symbol in self.nse_stocks:
            data = self.fetch_historical_data(symbol, period=period)
            if data is not None:
                all_data[symbol] = data

        if not all_data:
            logger.error("❌ No data fetched. Network restrictions may apply.")
            return None

        logger.info(f"\n✅ Fetched data for {len(all_data)} stocks")

        # Run day-by-day backtest
        total_days = min([len(d['prices']) for d in all_data.values()])
        start_day = max(30, total_days - days_to_test)  # Need 30 days history minimum

        logger.info(f"\n🔄 Running backtest from day {start_day} to {total_days-1}")
        logger.info(f"   (~{total_days - start_day} trading days)")

        daily_results = []

        for day in range(start_day, total_days - 1):
            best_trade = None

            # Analyze each stock for this day
            for symbol, data in all_data.items():
                hist_prices = data['prices'][:day+1]
                hist_volumes = data['volumes'][:day+1]

                if len(hist_prices) < 30:
                    continue

                signal = self.score_trade(hist_prices, hist_volumes)

                if signal['score'] >= self.min_score:
                    if best_trade is None or signal['score'] > best_trade['score']:
                        best_trade = {
                            'symbol': symbol,
                            'day_index': day,
                            'date': data['dates'][day],
                            'signal': signal,
                            'next_day_high': data['high'][day+1],
                            'next_day_low': data['low'][day+1],
                            'next_day_close': data['prices'][day+1],
                        }

            # Execute the best trade
            if best_trade:
                trade = self.simulate_trade(
                    entry=best_trade['signal']['current'],
                    predicted=best_trade['signal']['predicted'],
                    next_day_high=best_trade['next_day_high'],
                    next_day_low=best_trade['next_day_low'],
                    next_day_close=best_trade['next_day_close'],
                    direction=best_trade['signal']['direction'],
                )

                trade['symbol'] = best_trade['symbol']
                trade['date'] = best_trade['date']
                trade['score'] = best_trade['signal']['score']

                self.capital += trade['pnl']
                self.trade_history.append(trade)
                daily_results.append({
                    'date': best_trade['date'],
                    'trade': trade,
                    'capital': self.capital,
                })
            else:
                daily_results.append({
                    'date': all_data[list(all_data.keys())[0]]['dates'][day],
                    'trade': None,
                    'capital': self.capital,
                })

        return self.generate_report(daily_results)

    def generate_report(self, daily_results: list):
        """Generate comprehensive backtest report."""

        logger.info("\n" + "="*85)
        logger.info("📊 BACKTEST RESULTS")
        logger.info("="*85)

        if not self.trade_history:
            logger.warning("⚠️  No trades were executed")
            return None

        # Calculate metrics
        total_trades = len(self.trade_history)
        wins = [t for t in self.trade_history if t['pnl'] > 0]
        losses = [t for t in self.trade_history if t['pnl'] <= 0]
        target_hits = [t for t in self.trade_history if 'TARGET HIT' in t['outcome']]
        stop_losses = [t for t in self.trade_history if 'STOP LOSS' in t['outcome']]

        total_pnl = sum(t['pnl'] for t in self.trade_history)
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        max_win = max([t['pnl'] for t in self.trade_history])
        max_loss = min([t['pnl'] for t in self.trade_history])

        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        days_traded = len([r for r in daily_results if r['trade'] is not None])
        days_skipped = len([r for r in daily_results if r['trade'] is None])

        roi = ((self.capital - self.starting_capital) / self.starting_capital) * 100

        # Display summary
        logger.info(f"\n💰 PROFIT/LOSS SUMMARY:")
        logger.info(f"   Starting Capital:      ₹{self.starting_capital:,.2f}")
        logger.info(f"   Ending Capital:        ₹{self.capital:,.2f}")
        logger.info(f"   Total P&L:             ₹{total_pnl:+,.2f}")
        logger.info(f"   ROI:                   {roi:+.2f}%")

        logger.info(f"\n📊 TRADE STATISTICS:")
        logger.info(f"   Total Trading Days:    {len(daily_results)}")
        logger.info(f"   Days Traded:           {days_traded}")
        logger.info(f"   Days Skipped:          {days_skipped} (low confidence)")
        logger.info(f"   Total Trades:          {total_trades}")
        logger.info(f"   Wins:                  {len(wins)} ✅")
        logger.info(f"   Losses:                {len(losses)} ❌")
        logger.info(f"   Win Rate:              {win_rate:.1f}%")

        logger.info(f"\n🎯 OUTCOME BREAKDOWN:")
        logger.info(f"   Target Hits:           {len(target_hits)} ({len(target_hits)/total_trades*100:.1f}%)")
        logger.info(f"   Stop Losses:           {len(stop_losses)} ({len(stop_losses)/total_trades*100:.1f}%)")
        logger.info(f"   EOD Closes:            {total_trades - len(target_hits) - len(stop_losses)}")

        logger.info(f"\n💵 P&L ANALYSIS:")
        logger.info(f"   Average Win:           ₹{avg_win:+,.2f}")
        logger.info(f"   Average Loss:          ₹{avg_loss:+,.2f}")
        logger.info(f"   Largest Win:           ₹{max_win:+,.2f}")
        logger.info(f"   Largest Loss:          ₹{max_loss:+,.2f}")
        logger.info(f"   Risk/Reward Ratio:     1:{abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "   Risk/Reward: N/A")

        # Daily profit analysis
        if days_traded > 0:
            daily_avg_profit = total_pnl / days_traded
            monthly_estimate = daily_avg_profit * 20  # 20 trading days
            annual_estimate = daily_avg_profit * 250  # 250 trading days

            logger.info(f"\n📈 PROFIT ESTIMATES:")
            logger.info(f"   Avg per Trading Day:   ₹{daily_avg_profit:+,.2f}")
            logger.info(f"   Monthly Estimate:      ₹{monthly_estimate:+,.2f}")
            logger.info(f"   Annual Estimate:       ₹{annual_estimate:+,.2f}")

        # Show top stocks
        stock_pnl = {}
        for trade in self.trade_history:
            stock_pnl[trade['symbol']] = stock_pnl.get(trade['symbol'], 0) + trade['pnl']

        sorted_stocks = sorted(stock_pnl.items(), key=lambda x: x[1], reverse=True)

        logger.info(f"\n🏆 TOP PERFORMING STOCKS:")
        for symbol, pnl in sorted_stocks[:5]:
            count = len([t for t in self.trade_history if t['symbol'] == symbol])
            logger.info(f"   {symbol:<15} ₹{pnl:+,.2f} ({count} trades)")

        if len(sorted_stocks) > 5:
            logger.info(f"\n📉 WORST PERFORMING STOCKS:")
            for symbol, pnl in sorted_stocks[-3:]:
                count = len([t for t in self.trade_history if t['symbol'] == symbol])
                logger.info(f"   {symbol:<15} ₹{pnl:+,.2f} ({count} trades)")

        # Verdict
        logger.info("\n" + "="*85)
        if total_pnl > 0 and win_rate >= 50:
            logger.info("✅ STRATEGY VERDICT: PROFITABLE")
        elif total_pnl > 0:
            logger.info("⚠️  STRATEGY VERDICT: MARGINALLY PROFITABLE (low win rate)")
        else:
            logger.info("❌ STRATEGY VERDICT: NOT PROFITABLE (needs refinement)")
        logger.info("="*85)

        # Save results
        self.save_backtest_results(daily_results)

        return {
            'total_pnl': total_pnl,
            'roi': roi,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'capital_final': self.capital,
        }

    def save_backtest_results(self, daily_results: list):
        """Save detailed backtest results to JSON."""
        Path('backtest_results').mkdir(exist_ok=True)

        output = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'starting_capital': self.starting_capital,
                'profit_target': self.profit_target,
                'stop_loss_pct': self.stop_loss_pct,
                'min_score': self.min_score,
            },
            'summary': {
                'total_pnl': sum(t['pnl'] for t in self.trade_history),
                'total_trades': len(self.trade_history),
                'final_capital': self.capital,
                'roi_percent': ((self.capital - self.starting_capital) / self.starting_capital) * 100,
            },
            'trades': [
                {
                    'date': str(t['date']),
                    'symbol': t['symbol'],
                    'direction': t['direction'],
                    'entry': float(t['entry']),
                    'target': float(t['target']),
                    'quantity': t['quantity'],
                    'pnl': float(t['pnl']),
                    'outcome': t['outcome'],
                    'score': t['score'],
                }
                for t in self.trade_history
            ],
        }

        filename = f"backtest_results/backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        logger.info(f"\n💾 Backtest results saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Backtest Live Trading System')
    parser.add_argument('--period', default='6mo',
                       choices=['1mo', '3mo', '6mo', '1y', '2y'],
                       help='Historical data period (default: 6mo)')
    parser.add_argument('--days', type=int, default=60,
                       help='Number of days to backtest (default: 60)')
    parser.add_argument('--capital', type=float, default=200000,
                       help='Starting capital in INR (default: 200000)')
    parser.add_argument('--target', type=float, default=1000,
                       help='Profit target per trade (default: 1000)')
    parser.add_argument('--min-score', type=int, default=5,
                       help='Minimum signal score (0-10, default: 5)')
    parser.add_argument('--stop-loss', type=float, default=0.005,
                       help='Stop loss percentage (default: 0.005 = 0.5%%)')

    args = parser.parse_args()

    engine = BacktestEngine(
        profit_target=args.target,
        capital=args.capital,
        stop_loss_pct=args.stop_loss,
        min_score=args.min_score,
    )

    results = engine.run_backtest(period=args.period, days_to_test=args.days)

    if results:
        logger.info("\n✅ Backtest completed successfully")
    else:
        logger.error("\n❌ Backtest failed - check network access")


if __name__ == "__main__":
    main()
