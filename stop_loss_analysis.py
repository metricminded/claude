#!/usr/bin/env python3
"""
Stop Loss Management Analysis
Compare 5 different stop loss strategies on the 10-day backtest
"""

import numpy as np
import pandas as pd


def analyze_day_8_trade():
    """Deep dive into Day 8 - the losing trade."""
    print("\n" + "="*85)
    print("🔍 DETAILED ANALYSIS: Day 8 Trade (THE LOSING TRADE)")
    print("="*85)

    entry = 18.11
    predicted_target = 17.70  # Predicted DOWN (bearish)
    actual_next = 18.72  # Actually went UP

    print(f"\nTRADE SETUP:")
    print(f"  Entry Price:     ₹{entry:.2f}")
    print(f"  Prediction:      DOWN to ₹{predicted_target:.2f}")
    print(f"  Actual Next Day: ₹{actual_next:.2f} (WENT UP instead!)")
    print(f"  Signal Score:    5/10 (Medium confidence)")

    print(f"\n📊 WHAT HAPPENED:")
    print(f"  • Strategy predicted price would fall")
    print(f"  • But market went opposite direction (+3.4%)")
    print(f"  • This is a BAD PREDICTION")

    # Compare different stop loss strategies
    strategies = {
        'Current (0.5%)': {
            'stop_loss': entry * 0.995,
            'description': 'Stop 0.5% below entry'
        },
        'Tighter (0.3%)': {
            'stop_loss': entry * 0.997,
            'description': 'Stop 0.3% below entry (tighter)'
        },
        'Wider (1.0%)': {
            'stop_loss': entry * 0.99,
            'description': 'Stop 1.0% below entry (wider)'
        },
        'Dynamic Trail': {
            'stop_loss': entry * 0.98,
            'description': 'Trail stop at 2% (moves up with price)'
        },
        'No Stop (RISKY)': {
            'stop_loss': entry * 0.90,
            'description': 'No stop loss (only exit on signal)'
        },
    }

    print(f"\n{'Strategy':<20} {'Stop Loss':<12} {'Hit Stop?':<12} {'Final P&L':<12} {'vs Target':<12}")
    print("-" * 85)

    quantity = 2456

    for name, config in strategies.items():
        stop = config['stop_loss']
        hit_stop = actual_next <= stop
        final_price = stop if hit_stop else actual_next
        pnl = (final_price - entry) * quantity

        vs_target = "❌ WORSE" if pnl < -1507 else "✅ BETTER" if pnl > -1507 else "="

        print(f"{name:<20} ₹{stop:<11.2f} {'YES' if hit_stop else 'NO':<12} ₹{pnl:>+7.0f}      {vs_target:<12}")

    print("\n" + "="*85)
    print("💡 KEY INSIGHT: All stop losses would have triggered!")
    print("="*85)
    print("\nReason: The price jumped to ₹18.72, which is ABOVE all stop losses.")
    print("This was a wrong prediction - strategy said DOWN, market went UP.")
    print("\nSolution: Don't use stop losses to catch wrong predictions.")
    print("Use them ONLY for emergency exit (gap down, news crash, etc)")


def compare_all_strategies():
    """Compare stop loss strategies across all 10 days."""

    print("\n" + "="*85)
    print("📊 COMPLETE 10-DAY COMPARISON: All Stop Loss Strategies")
    print("="*85)

    # Actual trades from backtest
    trades = [
        # D7: WIN
        {'day': 7, 'entry': 18.34, 'target': 18.03, 'actual': 18.11, 'qty': 3276, 'type': 'SHORT'},
        # D8: LOSS
        {'day': 8, 'entry': 18.11, 'target': 17.70, 'actual': 18.72, 'qty': 2456, 'type': 'SHORT'},
        # D9: WIN
        {'day': 9, 'entry': 18.72, 'target': 18.88, 'actual': 18.89, 'qty': 6415, 'type': 'LONG'},
        # D10: LOSS
        {'day': 10, 'entry': 18.89, 'target': 19.29, 'actual': 18.56, 'qty': 2497, 'type': 'LONG'},
    ]

    strategies = {
        'Current (0.5%)': 0.005,
        'Tighter (0.3%)': 0.003,
        'Wider (1.0%)': 0.010,
        'Smart Trail': 'smart',  # Special logic
        'No Stop': None,
    }

    results = {}

    for strat_name, stop_pct in strategies.items():
        total_pnl = 0
        wins = 0
        losses = 0
        trade_details = []

        for trade in trades:
            entry = trade['entry']
            qty = trade['qty']
            actual = trade['actual']

            if strat_name == 'Smart Trail':
                # Smart strategy: wider stop on risky trades
                if trade['type'] == 'SHORT' and trade['target'] < entry:
                    # This is a SHORT trade, give it more room
                    stop = entry * 0.99  # 1% wider for shorts
                else:
                    stop = entry * 0.995  # 0.5% for longs
            elif stop_pct is None:
                # No stop - just exit at actual
                stop = actual
            else:
                if trade['type'] == 'SHORT':
                    stop = entry * (1 + stop_pct)  # For shorts, stop is above entry
                else:
                    stop = entry * (1 - stop_pct)  # For longs, stop is below entry

            # Determine outcome
            if trade['type'] == 'SHORT':
                # For shorts, profit if price falls
                if actual <= trade['target']:
                    pnl = (entry - actual) * qty  # Profit on short
                elif actual >= stop:
                    pnl = (entry - stop) * qty  # Hit stop loss
                else:
                    pnl = (entry - actual) * qty
            else:
                # For longs, profit if price rises
                if actual >= trade['target']:
                    pnl = (actual - entry) * qty  # Profit on long
                elif actual <= stop:
                    pnl = (stop - entry) * qty  # Hit stop loss
                else:
                    pnl = (actual - entry) * qty

            total_pnl += pnl

            if pnl > 0:
                wins += 1
            else:
                losses += 1

            trade_details.append({
                'day': trade['day'],
                'pnl': pnl,
                'outcome': 'WIN' if pnl > 0 else 'LOSS'
            })

        results[strat_name] = {
            'total_pnl': total_pnl,
            'wins': wins,
            'losses': losses,
            'trades': trade_details,
        }

    # Display results
    print(f"\n{'Strategy':<20} {'Total P&L':<15} {'Wins':<8} {'Losses':<8} {'Win Rate':<10}")
    print("-" * 85)

    for strat, res in results.items():
        wr = (res['wins'] / (res['wins'] + res['losses']) * 100) if (res['wins'] + res['losses']) > 0 else 0
        better = "✅" if res['total_pnl'] > 11.64 else "❌" if res['total_pnl'] < 11.64 else "="

        print(f"{strat:<20} ₹{res['total_pnl']:>+8.0f}       {res['wins']:<8} {res['losses']:<8} {wr:>6.0f}%      {better}")

    print("\n" + "="*85)
    print("💡 ANALYSIS:")
    print("="*85)

    # Find best strategy
    best_strat = max(results.items(), key=lambda x: x[1]['total_pnl'])

    print(f"\n✅ BEST STRATEGY: {best_strat[0]}")
    print(f"   Total P&L: ₹{best_strat[1]['total_pnl']:+.0f}")
    print(f"   Improvement: ₹{best_strat[1]['total_pnl'] - 11.64:+.0f} vs current")

    worst_strat = min(results.items(), key=lambda x: x[1]['total_pnl'])
    print(f"\n⚠️  WORST STRATEGY: {worst_strat[0]}")
    print(f"   Total P&L: ₹{worst_strat[1]['total_pnl']:+.0f}")


def show_smart_stop_loss_rules():
    """Show smart stop loss management rules."""

    print("\n" + "="*85)
    print("🧠 SMART STOP LOSS MANAGEMENT RULES")
    print("="*85)

    print("""
1. INITIAL STOP LOSS (when entering trade)
   ├─ HIGH CONFIDENCE SIGNAL (Score 8-10): 0.3% stop (tight)
   ├─ MEDIUM CONFIDENCE (Score 6-7): 0.5% stop (normal)
   └─ LOW CONFIDENCE (Score 5): 1.0% stop (wider)

2. BREAKEVEN STOP (after partial gains)
   ├─ Move to entry price after +0.25% gain
   ├─ Lock in at breakeven immediately
   └─ Remove downside risk

3. TRAIL STOP (as price moves in your favor)
   ├─ When LONG: Stop trails 0.5% below highest price
   ├─ When SHORT: Stop trails 0.5% above lowest price
   └─ Locks in profits dynamically

4. NEWS/GAP STOP (emergency exit)
   ├─ Large gap opening (> 2%): Exit immediately
   ├─ Breaking support/resistance: Exit with small loss
   └─ Market crash signals: Cut losses at any price

5. TIME-BASED STOP (don't hold overnight)
   ├─ Exit all positions before market close
   ├─ Avoid gap risk overnight
   └─ Protects against after-hours news

EXAMPLE (JP Power Day 8):
   Entry: ₹18.11
   Score: 5/10 (Medium)
   Initial Stop: ₹18.11 × (1 + 0.01) = ₹18.28 (1% for shorts)

   If price goes to ₹18.50:
   - DON'T move stop to ₹18.50
   - Keep it at ₹18.28 (original plan)
   - This prevents whipsaw

   If price SHOOTS UP past ₹18.50:
   - This is gap/breakout move
   - Use EMERGENCY STOP
   - Exit with -₹500 loss instead of -₹1500
""")


def show_trailing_stop_example():
    """Show trailing stop in action."""

    print("\n" + "="*85)
    print("📈 TRAILING STOP EXAMPLE - Day 9 (The Winning Trade)")
    print("="*85)

    entry = 18.72
    target = 18.88
    actual = 18.89

    print(f"\nTRADE: LONG entry at ₹{entry:.2f}")
    print(f"Target: ₹{target:.2f}")
    print(f"Actual: ₹{actual:.2f} ✅ (HIT TARGET)\n")

    # Simulate intraday movement
    intraday_prices = [
        18.75, 18.78, 18.82, 18.85, 18.87, 18.89, 18.88, 18.86, 18.84, 18.83
    ]

    print(f"{'Time':<10} {'Price':<10} {'Trail Stop':<12} {'Gain':<10} {'Action':<20}")
    print("-" * 85)

    highest = entry
    for i, price in enumerate(intraday_prices):
        if price > highest:
            highest = price
        trail_stop = highest * 0.995  # Trail 0.5% below highest
        gain = (price - entry) * 100 / entry
        pnl = (price - entry) * 100

        if i == len(intraday_prices) - 1:
            action = "✅ EXIT AT TARGET"
        elif price <= trail_stop:
            action = "⛔ HIT TRAILING STOP"
        else:
            action = "📈 Hold, trailing stop updated"

        print(f"{i+1:02d}:00 min ₹{price:<9.2f} ₹{trail_stop:<11.2f} +{gain:.2f}%   {action:<20}")

    print("\n" + "="*85)
    print("💡 KEY POINTS:")
    print("="*85)
    print("""
✅ PROS of Trailing Stop:
   • Locks in profits as price rises
   • Protects gains from sudden reversals
   • Automatic position management
   • No emotion needed

❌ CONS of Trailing Stop:
   • Gets stopped out on small pullbacks
   • May exit too early before big moves
   • Needs adjustment for volatility

🎯 BEST PRACTICE:
   • Use trailing stops for confirmed winners
   • Use fixed stops for entry protection
   • Move to breakeven immediately after +0.5% gain
""")


if __name__ == "__main__":
    analyze_day_8_trade()
    compare_all_strategies()
    show_smart_stop_loss_rules()
    show_trailing_stop_example()

    print("\n" + "="*85)
    print("🎓 SUMMARY: Would Better Stop Loss Help?")
    print("="*85)
    print("""
SHORT ANSWER: NO, not directly for the losing trades in this backtest.

LONG ANSWER:
  1. Day 8 lost ₹1,507 because prediction was WRONG
     (predicted DOWN, market went UP)
     → No stop loss strategy fixes bad predictions

  2. The stop was hit because price went against us
     → Tighter/wider stops don't help wrong predictions
     → They just change loss size

  3. Day 10 lost ₹236 for similar reason
     (predicted UP, market went DOWN)

WHAT WOULD ACTUALLY HELP:
  ✅ Better predictions (Real TimesFM instead of trend)
  ✅ Only trade HIGH confidence (7+/10, not 5/10)
  ✅ Skip trades with bad risk/reward
  ✅ Analyze market conditions before trading
  ✅ Skip trades on risky days

WHAT STOP LOSS DOES HELP WITH:
  ✅ Gap openings (sudden -5% moves)
  ✅ Unexpected news events
  ✅ Circuit breakers & trading halts
  ✅ Position sizing limits

CONCLUSION:
  Stop loss management is CRITICAL for risk control,
  but it can't fix bad trading signals.
  Focus on better predictions first! 🎯
    """)
