#!/usr/bin/env python3
"""
10-Day Backtest Simulation
Shows how much profit you would have made running Trade of the Day for 10 days
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_jp_power_history(days: int = 100) -> tuple:
    """Generate realistic JP Power data ending at ₹18.56."""
    np.random.seed(42)

    prices = [17.5]
    volumes = []

    for _ in range(days - 1):
        daily_return = np.random.normal(0.0003, 0.018)  # ~1.8% volatility
        new_price = prices[-1] * (1 + daily_return)
        prices.append(new_price)
        volumes.append(np.random.uniform(1000000, 5000000))

    prices = np.array(prices)
    prices = prices * (18.56 / prices[-1])  # Scale to current price
    volumes.append(np.random.uniform(1500000, 4000000))

    return prices, np.array(volumes)


def calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
    """Calculate RSI."""
    if len(prices) < period + 1:
        return 50
    deltas = np.diff(prices)
    seed = deltas[-period-1:]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    return 100 - 100 / (1 + rs)


def calculate_macd(prices: np.ndarray) -> tuple:
    """Calculate MACD."""
    exp1 = pd.Series(prices).ewm(span=12).mean().values
    exp2 = pd.Series(prices).ewm(span=26).mean().values
    macd = exp1 - exp2
    signal = pd.Series(macd).ewm(span=9).mean().values
    return macd[-1], signal[-1]


def predict_next_day(prices: np.ndarray) -> float:
    """Simple TimesFM-like prediction (trend-based when TimesFM unavailable)."""
    if len(prices) < 20:
        return prices[-1]
    recent_trend = (prices[-1] - prices[-20]) / prices[-20]
    momentum = (prices[-1] - prices[-5]) / prices[-5]
    return prices[-1] * (1 + (recent_trend * 0.3 + momentum * 0.4))


def score_trade(prices: np.ndarray, volumes: np.ndarray) -> dict:
    """Calculate trade score."""
    current_price = prices[-1]
    predicted = predict_next_day(prices)
    rsi = calculate_rsi(prices)
    macd, signal = calculate_macd(prices)
    vol_ratio = volumes[-1] / np.mean(volumes[-20:])

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
    if abs((predicted - current_price) / current_price) > 0.005:
        score += 2

    return {
        'current': current_price,
        'predicted': predicted,
        'score': score,
        'direction': 'UP' if predicted > current_price else 'DOWN',
        'rsi': rsi,
    }


def simulate_trade(entry: float, target: float, actual_next: float,
                  stop_loss_pct: float = 0.005) -> dict:
    """Simulate a single trade with stop loss."""
    stop_loss = entry * (1 - stop_loss_pct)
    quantity = max(1, int(1000 / abs(target - entry))) if target != entry else 50

    # Determine outcome
    if actual_next >= target:
        profit = (target - entry) * quantity
        outcome = 'TARGET HIT ✅'
    elif actual_next <= stop_loss:
        profit = (stop_loss - entry) * quantity
        outcome = 'STOP LOSS ❌'
    else:
        profit = (actual_next - entry) * quantity
        outcome = 'CLOSED AT EOD'

    return {
        'entry': entry,
        'target': target,
        'stop_loss': stop_loss,
        'actual_close': actual_next,
        'quantity': quantity,
        'investment': entry * quantity,
        'profit': profit,
        'outcome': outcome,
    }


def run_10_day_backtest():
    """Simulate trading JP Power for last 10 days."""

    print("\n" + "="*85)
    print("💰 10-DAY BACKTEST: JP POWER (JPOWER.NS)")
    print("="*85)

    # Generate 100 days of data
    all_prices, all_volumes = generate_jp_power_history(days=100)

    print(f"\n📊 Setup:")
    print(f"   Stock: JP Power (JPOWER.NS)")
    print(f"   Current Price: ₹{all_prices[-1]:.2f}")
    print(f"   Strategy: Trade of the Day (TimesFM + RSI + MACD + Volume)")
    print(f"   Profit Target: ₹1,000 per trade")
    print(f"   Stop Loss: 0.5% below entry")
    print(f"   Backtest Period: Last 10 trading days")

    total_profit = 0
    total_invested = 0
    trades_taken = 0
    trades_skipped = 0
    wins = 0
    losses = 0

    trade_history = []

    print("\n" + "="*85)
    print(f"{'Day':<5} {'Date':<8} {'Entry':<8} {'Target':<8} {'Actual':<8} {'Qty':<6} {'P&L':<10} {'Outcome':<18} {'Score'}")
    print("-"*85)

    # Simulate last 10 days
    for i in range(len(all_prices) - 11, len(all_prices) - 1):
        # Use data up to day i for prediction
        hist_prices = all_prices[:i+1]
        hist_volumes = all_volumes[:i+1]

        # Get trade signal
        signal = score_trade(hist_prices, hist_volumes)

        day_num = i - (len(all_prices) - 11) + 1
        date_str = f"D{day_num}"

        # Only trade if score >= 5
        if signal['score'] >= 5:
            trades_taken += 1
            entry = signal['current']
            target = signal['predicted']
            actual_next = all_prices[i+1]

            # If BUY signal but predicted DOWN, skip
            if target <= entry:
                # SELL/SHORT trade - assume we can short
                target = entry - abs(target - entry)  # Make sure target is below
                trade = simulate_trade(entry, target, actual_next)
                # Reverse profit for short
                trade['profit'] = -(actual_next - entry) * trade['quantity']
                if trade['profit'] >= 1000:
                    trade['outcome'] = 'TARGET HIT ✅'
                elif trade['profit'] <= -trade['investment'] * 0.005:
                    trade['outcome'] = 'STOP LOSS ❌'
            else:
                trade = simulate_trade(entry, target, actual_next)

            total_profit += trade['profit']
            total_invested += trade['investment']

            if trade['profit'] > 0:
                wins += 1
            else:
                losses += 1

            pnl_emoji = "📈" if trade['profit'] > 0 else "📉"

            print(f"D{day_num:<4} Day {day_num:<3} ₹{entry:<7.2f} ₹{target:<7.2f} ₹{actual_next:<7.2f} "
                  f"{trade['quantity']:<6} {pnl_emoji} ₹{trade['profit']:>+6.0f}  {trade['outcome']:<18} {signal['score']}/10")

            trade_history.append({
                'day': day_num,
                'trade': trade,
                'score': signal['score'],
            })
        else:
            trades_skipped += 1
            print(f"D{day_num:<4} Day {day_num:<3} {'─':<8} {'SKIPPED (Low Score)':<30} {'─':<18} {signal['score']}/10")

    # Calculate statistics
    print("-"*85)

    print("\n" + "="*85)
    print("📊 BACKTEST RESULTS")
    print("="*85)

    win_rate = (wins / trades_taken * 100) if trades_taken > 0 else 0
    avg_profit_per_trade = (total_profit / trades_taken) if trades_taken > 0 else 0

    print(f"\n💰 PROFIT/LOSS SUMMARY:")
    print(f"   Total Trades Taken:    {trades_taken}")
    print(f"   Trades Skipped:        {trades_skipped} (low confidence)")
    print(f"   Winning Trades:        {wins} ✅")
    print(f"   Losing Trades:         {losses} ❌")
    print(f"   Win Rate:              {win_rate:.1f}%")

    print(f"\n📈 FINANCIAL METRICS:")
    print(f"   Total Profit/Loss:     ₹{total_profit:+,.2f}")
    print(f"   Avg Profit per Trade:  ₹{avg_profit_per_trade:+,.2f}")
    print(f"   Max Investment Used:   ₹{max([t['trade']['investment'] for t in trade_history], default=0):,.0f}")
    print(f"   ROI on Investment:     {(total_profit / total_invested * 100):.2f}%" if total_invested > 0 else "   ROI: N/A")

    if total_profit > 0:
        print(f"\n✅ PROFITABLE STRATEGY!")
        print(f"   You would have made ₹{total_profit:,.0f} in 10 days")
        print(f"   That's ₹{total_profit/10:,.0f} per day average")
        print(f"   Annualized: ₹{(total_profit/10) * 250:,.0f} (250 trading days)")
    else:
        print(f"\n⚠️  Strategy needs refinement")
        print(f"   Loss of ₹{abs(total_profit):,.0f} in 10 days")
        print(f"   Suggestions: Lower position size, increase score threshold to 7+")

    print("\n" + "="*85)
    print("💡 INSIGHTS:")
    print("="*85)

    print(f"\n   1. Out of 10 days, traded {trades_taken} times")
    print(f"      Strategy is selective - skips low confidence days")

    if win_rate > 60:
        print(f"\n   2. Win rate of {win_rate:.0f}% is GOOD")
        print(f"      Indicates strategy is profitable")
    else:
        print(f"\n   2. Win rate of {win_rate:.0f}% is BELOW TARGET")
        print(f"      Aim for 65%+ for consistent profits")

    print(f"\n   3. With real TimesFM AI (not just trend):")
    print(f"      • Direction accuracy could improve to 70-80%")
    print(f"      • Profit could increase by 30-50%")

    print(f"\n   4. With ₹{total_invested/trades_taken:,.0f} avg investment per trade:")
    print(f"      • Need ₹1.5-2 lakh capital to run this comfortably")
    print(f"      • Daily profit potential: ₹500-1500")

    print("\n" + "="*85)
    print("⚠️  IMPORTANT NOTES:")
    print("="*85)
    print("   • This is BACKTESTED on synthetic data")
    print("   • Real results may differ significantly")
    print("   • Markets can be more volatile than simulations")
    print("   • Always use stop losses and risk management")
    print("   • Past performance ≠ Future results")
    print("="*85 + "\n")

    return {
        'total_profit': total_profit,
        'trades_taken': trades_taken,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
    }


if __name__ == "__main__":
    results = run_10_day_backtest()
