#!/usr/bin/env python3
"""
Kite Connect Integration for Live Trading System
Uses Zerodha's Kite Connect API for real NSE market data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import json
import os
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from kiteconnect import KiteConnect
    KITE_AVAILABLE = True
except ImportError:
    KITE_AVAILABLE = False
    logger.warning("⚠️  kiteconnect not installed. Run: pip install kiteconnect")


class KiteDataProvider:
    """Fetch NSE market data using Kite Connect API."""

    def __init__(self, api_key: str = None, access_token: str = None):
        """
        Initialize Kite Connect client.

        Args:
            api_key: Your Kite Connect API key
            access_token: Daily access token (from login flow)
        """
        if not KITE_AVAILABLE:
            raise ImportError("Install kiteconnect: pip install kiteconnect")

        # Load credentials from environment or config
        self.api_key = api_key or os.getenv('KITE_API_KEY')
        self.access_token = access_token or os.getenv('KITE_ACCESS_TOKEN')

        if not self.api_key:
            raise ValueError(
                "KITE_API_KEY not found. Set environment variable or pass api_key.\n"
                "Get your API key from: https://developers.kite.trade/"
            )

        self.kite = KiteConnect(api_key=self.api_key)

        if self.access_token:
            self.kite.set_access_token(self.access_token)
            logger.info("✅ Kite Connect initialized with access token")
        else:
            logger.warning("⚠️  No access token. Run authentication first.")

        # Cache for instrument tokens
        self._instruments_cache = None

    def login_url(self) -> str:
        """Get Kite Connect login URL for authentication."""
        return self.kite.login_url()

    def authenticate(self, request_token: str, api_secret: str) -> str:
        """
        Generate access token from request token.

        Args:
            request_token: Got from login redirect URL
            api_secret: Your API secret

        Returns:
            Access token (valid for 1 day)
        """
        data = self.kite.generate_session(request_token, api_secret=api_secret)
        self.access_token = data['access_token']
        self.kite.set_access_token(self.access_token)
        logger.info(f"✅ Authenticated. Access token: {self.access_token[:10]}...")

        # Save token to file for reuse
        with open('.kite_token', 'w') as f:
            json.dump({
                'access_token': self.access_token,
                'created': datetime.now().isoformat()
            }, f)

        return self.access_token

    def get_instruments(self, exchange: str = "NSE") -> pd.DataFrame:
        """Get all NSE instruments with their tokens."""
        if self._instruments_cache is None:
            logger.info(f"📥 Fetching {exchange} instruments...")
            instruments = self.kite.instruments(exchange)
            self._instruments_cache = pd.DataFrame(instruments)
            logger.info(f"✅ Got {len(self._instruments_cache)} instruments")
        return self._instruments_cache

    def get_instrument_token(self, symbol: str) -> Optional[int]:
        """Get instrument token for a symbol (e.g., 'RELIANCE')."""
        # Remove .NS suffix if present
        symbol = symbol.replace('.NS', '')

        instruments = self.get_instruments()
        match = instruments[
            (instruments['tradingsymbol'] == symbol) &
            (instruments['exchange'] == 'NSE')
        ]

        if match.empty:
            logger.warning(f"⚠️  Symbol not found: {symbol}")
            return None

        return int(match.iloc[0]['instrument_token'])

    def get_historical_data(self, symbol: str, days: int = 90,
                            interval: str = "day") -> Optional[pd.DataFrame]:
        """
        Fetch real historical data from Kite Connect.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE' or 'JPOWER')
            days: Number of days of history
            interval: 'minute', '3minute', '5minute', '15minute', '30minute', '60minute', 'day'

        Returns:
            DataFrame with OHLCV data
        """
        token = self.get_instrument_token(symbol)
        if token is None:
            return None

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            logger.info(f"📥 Fetching {symbol} ({days} days, {interval})...")
            data = self.kite.historical_data(
                instrument_token=token,
                from_date=start_date.strftime('%Y-%m-%d'),
                to_date=end_date.strftime('%Y-%m-%d'),
                interval=interval
            )

            if not data:
                logger.warning(f"⚠️  No data for {symbol}")
                return None

            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            logger.info(f"✅ Got {len(df)} data points")
            return df

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current LTP (Last Traded Price)."""
        symbol = symbol.replace('.NS', '')
        try:
            quote = self.kite.ltp(f"NSE:{symbol}")
            return quote[f"NSE:{symbol}"]['last_price']
        except Exception as e:
            logger.error(f"❌ Error fetching LTP for {symbol}: {e}")
            return None

    def get_quote(self, symbol: str) -> Optional[dict]:
        """Get full quote with bid/ask/volume."""
        symbol = symbol.replace('.NS', '')
        try:
            quote = self.kite.quote(f"NSE:{symbol}")
            return quote[f"NSE:{symbol}"]
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None


class KiteBacktest:
    """Backtest using real Kite Connect data."""

    def __init__(self, kite_provider: KiteDataProvider,
                 capital: float = 200000,
                 profit_target: float = 1000,
                 stop_loss_pct: float = 0.005,
                 min_score: int = 5):
        self.kite = kite_provider
        self.starting_capital = capital
        self.capital = capital
        self.profit_target = profit_target
        self.stop_loss_pct = stop_loss_pct
        self.min_score = min_score
        self.trade_history = []

        self.stocks = [
            'JPOWER', 'RELIANCE', 'TCS', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'WIPRO', 'KOTAKBANK', 'LT', 'MARUTI',
            'SUNPHARMA', 'ASIANPAINT', 'HCLTECH', 'SBIN',
            'BHARTIARTL', 'ITC', 'TITAN', 'M&M', 'NESTLEIND',
        ]

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
        try:
            from timesfm import TimesFM
            tfm = TimesFM(context_len=512, prediction_len=1, num_layers=20)
            ts_input = np.array([prices.astype(np.float32)])
            forecast = tfm.forecast(ts_input, num_samples=100)
            return float(np.mean(forecast, axis=0)[0])
        except:
            recent_trend = (prices[-1] - prices[-20]) / prices[-20] if len(prices) >= 20 else 0
            return prices[-1] * (1 + recent_trend * 0.3)

    def score_trade(self, prices: np.ndarray, volumes: np.ndarray) -> dict:
        current = float(prices[-1])
        predicted = self.predict_next_day(prices)
        rsi = self.calculate_rsi(prices)
        macd, signal = self.calculate_macd(prices)
        vol_ratio = volumes[-1] / np.mean(volumes[-20:]) if len(volumes) >= 20 else 1.0

        score = 0
        if predicted > current:
            score += 2
        if rsi < 30:
            score += 2
        elif 30 < rsi < 70:
            score += 1
        if macd > signal:
            score += 2
        if vol_ratio > 1.5:
            score += 2
        if abs((predicted - current) / current) * 100 > 1:
            score += 2

        return {
            'current': current,
            'predicted': predicted,
            'direction': 'UP' if predicted > current else 'DOWN',
            'score': score,
            'rsi': rsi,
        }

    def run_backtest(self, days: int = 90):
        """Run backtest on real Kite Connect data."""
        print("\n" + "="*85)
        print("📊 KITE CONNECT BACKTEST - Real NSE Data")
        print("="*85)
        print(f"Capital: ₹{self.starting_capital:,.0f}")
        print(f"Target: ₹{self.profit_target}")
        print(f"Days: {days}")
        print(f"Stocks: {len(self.stocks)}")

        # Fetch real data for all stocks
        all_data = {}
        for symbol in self.stocks:
            df = self.kite.get_historical_data(symbol, days=days+30)
            if df is not None and len(df) > 30:
                all_data[symbol] = df

        if not all_data:
            print("❌ No data fetched. Check Kite Connect credentials.")
            return None

        print(f"\n✅ Got data for {len(all_data)} stocks")
        print(f"\n🔄 Running backtest...")

        # Day-by-day simulation
        min_days = min(len(df) for df in all_data.values())
        start_idx = 30

        for day in range(start_idx, min_days - 1):
            best_trade = None

            for symbol, df in all_data.items():
                if day >= len(df) - 1:
                    continue

                prices = df['close'].values[:day+1]
                volumes = df['volume'].values[:day+1]

                signal = self.score_trade(prices, volumes)

                if signal['score'] >= self.min_score:
                    if best_trade is None or signal['score'] > best_trade['signal']['score']:
                        best_trade = {
                            'symbol': symbol,
                            'day': day,
                            'date': df.index[day],
                            'signal': signal,
                            'next_high': df['high'].iloc[day+1],
                            'next_low': df['low'].iloc[day+1],
                            'next_close': df['close'].iloc[day+1],
                        }

            if best_trade:
                trade = self.execute_trade(best_trade)
                self.capital += trade['pnl']
                self.trade_history.append(trade)

        return self.print_report()

    def execute_trade(self, trade_data: dict) -> dict:
        signal = trade_data['signal']
        entry = signal['current']
        predicted = signal['predicted']
        direction = signal['direction']

        expected_move = abs(predicted - entry)
        quantity = max(1, int(self.profit_target / expected_move)) if expected_move > 0 else 50
        quantity = min(quantity, int(self.capital * 0.5 / entry))

        if direction == 'UP':
            target = predicted
            stop = entry * (1 - self.stop_loss_pct)
            if trade_data['next_high'] >= target:
                pnl = (target - entry) * quantity
                outcome = 'TARGET HIT'
            elif trade_data['next_low'] <= stop:
                pnl = (stop - entry) * quantity
                outcome = 'STOP LOSS'
            else:
                pnl = (trade_data['next_close'] - entry) * quantity
                outcome = 'EOD CLOSE'
        else:
            target = predicted
            stop = entry * (1 + self.stop_loss_pct)
            if trade_data['next_low'] <= target:
                pnl = (entry - target) * quantity
                outcome = 'TARGET HIT'
            elif trade_data['next_high'] >= stop:
                pnl = (entry - stop) * quantity
                outcome = 'STOP LOSS'
            else:
                pnl = (entry - trade_data['next_close']) * quantity
                outcome = 'EOD CLOSE'

        return {
            'date': trade_data['date'],
            'symbol': trade_data['symbol'],
            'direction': direction,
            'entry': entry,
            'target': target,
            'stop': stop,
            'quantity': quantity,
            'pnl': pnl,
            'outcome': outcome,
            'score': signal['score'],
        }

    def print_report(self):
        if not self.trade_history:
            print("⚠️  No trades executed")
            return None

        wins = [t for t in self.trade_history if t['pnl'] > 0]
        losses = [t for t in self.trade_history if t['pnl'] <= 0]
        total_pnl = sum(t['pnl'] for t in self.trade_history)
        win_rate = len(wins) / len(self.trade_history) * 100
        roi = ((self.capital - self.starting_capital) / self.starting_capital) * 100

        print("\n" + "="*85)
        print("📊 BACKTEST RESULTS")
        print("="*85)
        print(f"\n💰 P&L Summary:")
        print(f"   Starting: ₹{self.starting_capital:,.2f}")
        print(f"   Ending:   ₹{self.capital:,.2f}")
        print(f"   Total:    ₹{total_pnl:+,.2f}")
        print(f"   ROI:      {roi:+.2f}%")
        print(f"\n📊 Stats:")
        print(f"   Trades:   {len(self.trade_history)}")
        print(f"   Wins:     {len(wins)}")
        print(f"   Losses:   {len(losses)}")
        print(f"   Win Rate: {win_rate:.1f}%")

        # Save
        Path('backtest_results').mkdir(exist_ok=True)
        filename = f"backtest_results/kite_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'summary': {'total_pnl': total_pnl, 'roi': roi, 'win_rate': win_rate},
                'trades': [{**t, 'date': str(t['date'])} for t in self.trade_history],
            }, f, indent=2, default=str)
        print(f"\n💾 Saved to {filename}")

        return {'total_pnl': total_pnl, 'roi': roi, 'win_rate': win_rate}


def authenticate_kite():
    """Interactive Kite Connect authentication helper."""
    print("\n" + "="*70)
    print("🔐 KITE CONNECT AUTHENTICATION")
    print("="*70)

    if not KITE_AVAILABLE:
        print("❌ Install first: pip install kiteconnect")
        return

    api_key = input("\nEnter your Kite API Key: ").strip()
    api_secret = input("Enter your Kite API Secret: ").strip()

    if not api_key or not api_secret:
        print("❌ API Key and Secret required")
        return

    kite = KiteDataProvider(api_key=api_key)
    login_url = kite.login_url()

    print(f"\n📋 Step 1: Open this URL in browser:")
    print(f"   {login_url}")
    print(f"\n📋 Step 2: Login with Zerodha credentials")
    print(f"📋 Step 3: After login, you'll be redirected to a URL")
    print(f"📋 Step 4: Copy the 'request_token' from the URL")

    request_token = input("\nEnter request_token from redirect URL: ").strip()

    try:
        access_token = kite.authenticate(request_token, api_secret)
        print(f"\n✅ SUCCESS!")
        print(f"\nAccess Token: {access_token}")
        print(f"\n💡 Save these to your environment:")
        print(f"   export KITE_API_KEY='{api_key}'")
        print(f"   export KITE_ACCESS_TOKEN='{access_token}'")
        print(f"\n⚠️  Token valid for 1 day. Re-authenticate daily.")
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'auth':
        authenticate_kite()
    elif len(sys.argv) > 1 and sys.argv[1] == 'backtest':
        # Run backtest with Kite data
        try:
            kite = KiteDataProvider()
            backtest = KiteBacktest(kite, capital=200000)
            backtest.run_backtest(days=90)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n💡 First authenticate:")
            print("   python kite_connect_integration.py auth")
    else:
        print("\n" + "="*70)
        print("📊 KITE CONNECT INTEGRATION")
        print("="*70)
        print("\nUsage:")
        print("  1. Authenticate (first time):")
        print("     python kite_connect_integration.py auth")
        print("\n  2. Run backtest with real data:")
        print("     python kite_connect_integration.py backtest")
        print("\n  3. Use in your code:")
        print("     from kite_connect_integration import KiteDataProvider")
        print("     kite = KiteDataProvider()")
        print("     data = kite.get_historical_data('RELIANCE', days=90)")
        print("="*70)
