#!/usr/bin/env python3
"""
BACKTEST DEMO with Realistic Synthetic Data
Simulates 6 months of NSE trading - shows what the real backtest would look like
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class RealisticBacktest:
    """Backtest with realistic market simulation."""

    def __init__(self, capital: float = 200000, profit_target: float = 1000,
                 stop_loss_pct: float = 0.005, min_score: int = 5):
        self.starting_capital = capital
        self.capital = capital
        self.profit_target = profit_target
        self.stop_loss_pct = stop_loss_pct
        self.min_score = min_score
        self.trade_history = []

        # Realistic NSE stocks with current prices
        self.stocks = {
            'JPOWER.NS': {'price': 18.56, 'volatility': 0.025},
            'RELIANCE.NS': {'price': 2450, 'volatility': 0.015},
            'TCS.NS': {'price': 3600, 'volatility': 0.012},
            'INFOSY.NS': {'price': 1850, 'volatility': 0.015},
            'ICICIBANK.NS': {'price': 1080, 'volatility': 0.018},
            'HINDUNILVR.NS': {'price': 2400, 'volatility': 0.012},
            'WIPRO.NS': {'price': 290, 'volatility': 0.020},
            'KOTAK.NS': {'price': 1750, 'volatility': 0.016},
            'LT.NS': {'price': 3500, 'volatility': 0.014},
            'MARUTI.NS': {'price': 11000, 'volatility': 0.018},
            'SUNPHARMA.NS': {'price': 1450, 'volatility': 0.020},
            'ASIANPAINT.NS': {'price': 2850, 'volatility': 0.013},
            'HCLTECH.NS': {'price': 1480, 'volatility': 0.014},
            'SBIN.NS': {'price': 750, 'volatility': 0.020},
            'BHARTIARTL.NS': {'price': 1320, 'volatility': 0.015},
            'ITC.NS': {'price': 450, 'volatility': 0.012},
            'TITAN.NS': {'price': 3200, 'volatility': 0.016},
            'M&M.NS': {'price': 2800, 'volatility': 0.018},
            'NESTLEIND.NS': {'price': 2200, 'volatility': 0.011},
        }

    def generate_historical_data(self, symbol: str, days: int = 180) -> dict:
        """Generate realistic historical OHLC data."""
        np.random.seed(hash(symbol) % 2**32)

        config = self.stocks[symbol]
        current_price = config['price']
        volatility = config['volatility']

        # Generate prices working backwards
        prices = [current_price]
        for _ in range(days - 1):
            daily_return = np.random.normal(0.0005, volatility)
            new_price = prices[-1] * (1 + daily_return)
            prices.append(new_price)

        prices = np.array(prices[::-1])  # Reverse to chronological
        prices = prices * (current_price / prices[-1])  # Scale to end at current

        # Generate OHLC and volume
        highs = prices * (1 + np.abs(np.random.normal(0, volatility/2, days)))
        lows = prices * (1 - np.abs(np.random.normal(0, volatility/2, days)))
        opens = prices * (1 + np.random.normal(0, volatility/3, days))
        volumes = np.random.uniform(500000, 5000000, days)

        # Add volume spikes occasionally
        spike_days = np.random.choice(days, size=days//20, replace=False)
        volumes[spike_days] *= np.random.uniform(1.5, 3.0, len(spike_days))

        return {
            'symbol': symbol,
            'prices': prices,
            'highs': highs,
            'lows': lows,
            'opens': opens,
            'volumes': volumes,
        }

    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50
        deltas = np.diff(prices)
        seed = deltas[-period-1:]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        return 100 - 100 / (1 + rs)

    def calculate_macd(self, prices: np.ndarray) -> tuple:
        if len(prices) < 26:
            return 0, 0
        exp1 = pd.Series(prices).ewm(span=12).mean().values
        exp2 = pd.Series(prices).ewm(span=26).mean().values
        macd = exp1 - exp2
        signal = pd.Series(macd).ewm(span=9).mean().values
        return macd[-1], signal[-1]

    def predict_next_day(self, prices: np.ndarray) -> float:
        """Simulate TimesFM prediction."""
        recent_trend = (prices[-1] - prices[-20]) / prices[-20] if len(prices) >= 20 else 0
        momentum = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
        # Add some prediction noise to simulate model behavior
        noise = np.random.normal(0, 0.003)
        return prices[-1] * (1 + (recent_trend * 0.3 + momentum * 0.4) + noise)

    def score_trade(self, prices: np.ndarray, volumes: np.ndarray) -> dict:
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
        }

    def execute_trade(self, signal: dict, next_high: float, next_low: float,
                      next_close: float) -> dict:
        entry = signal['current']
        predicted = signal['predicted']
        direction = signal['direction']

        expected_move = abs(predicted - entry)
        quantity = max(1, int(self.profit_target / expected_move)) if expected_move > 0 else 50
        max_qty = int(self.capital * 0.5 / entry)
        quantity = min(quantity, max_qty)

        investment = entry * quantity

        if direction == 'UP':
            target = predicted
            stop_loss = entry * (1 - self.stop_loss_pct)

            if next_high >= target:
                pnl = (target - entry) * quantity
                outcome = 'TARGET HIT'
            elif next_low <= stop_loss:
                pnl = (stop_loss - entry) * quantity
                outcome = 'STOP LOSS'
            else:
                pnl = (next_close - entry) * quantity
                outcome = 'EOD CLOSE'
        else:
            target = predicted
            stop_loss = entry * (1 + self.stop_loss_pct)

            if next_low <= target:
                pnl = (entry - target) * quantity
                outcome = 'TARGET HIT'
            elif next_high >= stop_loss:
                pnl = (entry - stop_loss) * quantity
                outcome = 'STOP LOSS'
            else:
                pnl = (entry - next_close) * quantity
                outcome = 'EOD CLOSE'

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

    def run(self, days: int = 120):
        """Run backtest simulation."""
        print("\n" + "="*85)
        print("📊 BACKTEST SIMULATION - Live Trading System")
        print("="*85)
        print(f"Mode:              SYNTHETIC DATA (simulating 6 months of real trading)")
        print(f"Starting Capital:  ₹{self.starting_capital:,.0f}")
        print(f"Profit Target:     ₹{self.profit_target}")
        print(f"Stop Loss:         {self.stop_loss_pct*100}%")
        print(f"Min Score:         {self.min_score}/10")
        print(f"Stocks:            {len(self.stocks)}")
        print(f"Testing Days:      {days}")
        print("\n📥 Generating historical data...")

        # Generate data for all stocks
        all_data = {}
        for symbol in self.stocks.keys():
            all_data[symbol] = self.generate_historical_data(symbol, days=180)

        print(f"✅ Generated data for {len(all_data)} stocks")
        print(f"\n🔄 Running backtest day-by-day...")

        start_day = 30  # Need 30 days history
        end_day = min(start_day + days, 179)

        daily_capital = [self.capital]

        for day in range(start_day, end_day):
            best_trade = None

            for symbol, data in all_data.items():
                hist_prices = data['prices'][:day+1]
                hist_volumes = data['volumes'][:day+1]

                signal = self.score_trade(hist_prices, hist_volumes)

                if signal['score'] >= self.min_score:
                    if best_trade is None or signal['score'] > best_trade['signal']['score']:
                        best_trade = {
                            'symbol': symbol,
                            'day': day,
                            'signal': signal,
                            'next_high': data['highs'][day+1],
                            'next_low': data['lows'][day+1],
                            'next_close': data['prices'][day+1],
                        }

            if best_trade:
                trade = self.execute_trade(
                    best_trade['signal'],
                    best_trade['next_high'],
                    best_trade['next_low'],
                    best_trade['next_close'],
                )
                trade['symbol'] = best_trade['symbol']
                trade['day'] = best_trade['day']
                trade['score'] = best_trade['signal']['score']

                self.capital += trade['pnl']
                self.trade_history.append(trade)

            daily_capital.append(self.capital)

        self.print_results(daily_capital)
        self.save_results()

    def print_results(self, daily_capital: list):
        """Print comprehensive results."""
        print("\n" + "="*85)
        print("📊 BACKTEST RESULTS")
        print("="*85)

        if not self.trade_history:
            print("⚠️  No trades executed")
            return

        # Calculate metrics
        total_trades = len(self.trade_history)
        wins = [t for t in self.trade_history if t['pnl'] > 0]
        losses = [t for t in self.trade_history if t['pnl'] <= 0]
        target_hits = [t for t in self.trade_history if t['outcome'] == 'TARGET HIT']
        stop_losses = [t for t in self.trade_history if t['outcome'] == 'STOP LOSS']
        eod_closes = [t for t in self.trade_history if t['outcome'] == 'EOD CLOSE']

        total_pnl = sum(t['pnl'] for t in self.trade_history)
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        max_win = max([t['pnl'] for t in self.trade_history])
        max_loss = min([t['pnl'] for t in self.trade_history])

        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        roi = ((self.capital - self.starting_capital) / self.starting_capital) * 100

        # Recent trades (last 10)
        print("\n📋 RECENT TRADES (Last 10):")
        print(f"\n{'Day':<5} {'Symbol':<15} {'Dir':<5} {'Entry':<10} {'Target':<10} {'P&L':<12} {'Outcome':<12} {'Score'}")
        print("-" * 85)

        for trade in self.trade_history[-10:]:
            pnl_str = f"₹{trade['pnl']:+,.0f}"
            emoji = "✅" if trade['pnl'] > 0 else "❌"
            print(f"D{trade['day']:<4} {trade['symbol']:<15} {trade['direction']:<5} "
                  f"₹{trade['entry']:<9.2f} ₹{trade['target']:<9.2f} {pnl_str:<10} {emoji} "
                  f"{trade['outcome']:<10} {trade['score']}/10")

        # Profit/Loss Summary
        print("\n" + "="*85)
        print("💰 PROFIT/LOSS SUMMARY")
        print("="*85)
        print(f"   Starting Capital:      ₹{self.starting_capital:>15,.2f}")
        print(f"   Ending Capital:        ₹{self.capital:>15,.2f}")
        print(f"   Total P&L:             ₹{total_pnl:>+15,.2f}")
        print(f"   ROI:                    {roi:>+15.2f}%")

        print("\n📊 TRADE STATISTICS:")
        print(f"   Total Days Tested:     {len(daily_capital)-1:>15}")
        print(f"   Total Trades:          {total_trades:>15}")
        print(f"   Wins:                  {len(wins):>15} ✅")
        print(f"   Losses:                {len(losses):>15} ❌")
        print(f"   Win Rate:              {win_rate:>14.1f}%")

        print("\n🎯 OUTCOME BREAKDOWN:")
        print(f"   🎯 Target Hits:        {len(target_hits):>15} ({len(target_hits)/total_trades*100:.1f}%)")
        print(f"   ⛔ Stop Losses:        {len(stop_losses):>15} ({len(stop_losses)/total_trades*100:.1f}%)")
        print(f"   📅 EOD Closes:         {len(eod_closes):>15} ({len(eod_closes)/total_trades*100:.1f}%)")

        print("\n💵 P&L ANALYSIS:")
        print(f"   Average Win:           ₹{avg_win:>+15,.2f}")
        print(f"   Average Loss:          ₹{avg_loss:>+15,.2f}")
        print(f"   Largest Win:           ₹{max_win:>+15,.2f}")
        print(f"   Largest Loss:          ₹{max_loss:>+15,.2f}")
        if avg_loss != 0:
            print(f"   Risk/Reward Ratio:     1:{abs(avg_win/avg_loss):.2f}")

        # Profit estimates
        days_traded = total_trades
        if days_traded > 0:
            daily_avg = total_pnl / days_traded
            monthly = daily_avg * 20
            annual = daily_avg * 250

            print("\n📈 PROFIT PROJECTIONS:")
            print(f"   Avg per Trade:         ₹{daily_avg:>+15,.2f}")
            print(f"   Monthly Estimate:      ₹{monthly:>+15,.2f}")
            print(f"   Annual Estimate:       ₹{annual:>+15,.2f}")

        # Top stocks
        stock_pnl = {}
        stock_counts = {}
        for trade in self.trade_history:
            stock_pnl[trade['symbol']] = stock_pnl.get(trade['symbol'], 0) + trade['pnl']
            stock_counts[trade['symbol']] = stock_counts.get(trade['symbol'], 0) + 1

        sorted_stocks = sorted(stock_pnl.items(), key=lambda x: x[1], reverse=True)

        print("\n🏆 TOP 5 PERFORMING STOCKS:")
        for symbol, pnl in sorted_stocks[:5]:
            print(f"   {symbol:<20} ₹{pnl:>+10,.0f} ({stock_counts[symbol]} trades)")

        if len(sorted_stocks) > 5:
            print("\n📉 WORST PERFORMING STOCKS:")
            for symbol, pnl in sorted_stocks[-3:]:
                print(f"   {symbol:<20} ₹{pnl:>+10,.0f} ({stock_counts[symbol]} trades)")

        # Verdict
        print("\n" + "="*85)
        if total_pnl > 0 and win_rate >= 55:
            print("✅ STRATEGY VERDICT: PROFITABLE - Ready for live deployment!")
        elif total_pnl > 0:
            print("⚠️  STRATEGY VERDICT: MARGINALLY PROFITABLE - Refine before live trading")
        else:
            print("❌ STRATEGY VERDICT: NOT PROFITABLE - Strategy needs improvement")
        print("="*85)

    def save_results(self):
        """Save results to JSON."""
        Path('backtest_results').mkdir(exist_ok=True)

        output = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'SYNTHETIC_DEMO',
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
                'wins': len([t for t in self.trade_history if t['pnl'] > 0]),
                'losses': len([t for t in self.trade_history if t['pnl'] <= 0]),
            },
            'trades': [{
                'day': t['day'],
                'symbol': t['symbol'],
                'direction': t['direction'],
                'entry': float(t['entry']),
                'target': float(t['target']),
                'quantity': int(t['quantity']),
                'pnl': float(t['pnl']),
                'outcome': t['outcome'],
                'score': int(t['score']),
            } for t in self.trade_history]
        }

        filename = f"backtest_results/demo_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        print(f"\n💾 Results saved to {filename}")


if __name__ == "__main__":
    # Run 120-day backtest (~6 months of trading)
    backtest = RealisticBacktest(
        capital=200000,
        profit_target=1000,
        stop_loss_pct=0.005,
        min_score=5,
    )

    backtest.run(days=120)

    print("\n" + "="*85)
    print("💡 NOTE: This is a DEMO with synthetic data")
    print("="*85)
    print("To run with REAL data:")
    print("  1. Deploy to server with internet access")
    print("  2. Run: python backtest_live_system.py --period 6mo --days 120")
    print("  3. Real yfinance data will give actual market performance")
    print("="*85 + "\n")
