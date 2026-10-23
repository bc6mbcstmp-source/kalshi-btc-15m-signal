# Kalshi BTC 15-minute Signal Watcher

This starter bot streams BTC/USDT 1-minute candles from Binance public market data and polls Kalshi's public API for the active `KXBTC15M` market. It displays an UP, DOWN, or NO TRADE indicator signal.

## Important limitations
- This is a starter indicator, not a proven trading strategy or financial advice.
- It does **not** place orders. It does not need Kalshi credentials.
- The indicator score is not a calibrated probability or a promise of accuracy.
- The external BTC/USDT feed may differ from the exact price source or settlement rule used by a Kalshi contract. Verify the specific contract's rules before relying on the signal.
- Public API fields and market availability can change; if the active market isn't found, the script deliberately says it is unconfirmed rather than inventing a ticker.
- Test and measure outcomes before risking money.

## Install
Python 3.10+ recommended.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python kalshi_btc_15m_bot.py
```

Press Ctrl+C to stop. Non-NO-TRADE signals are logged to `signals.csv`.

## How the signal works
- EMA(5) vs EMA(13) trend
- 1-minute and 5-minute momentum
- RSI(14) extreme-move filter
- Requires at least 2 of 3 directional checks to agree
- Returns NO TRADE when signals conflict or RSI suggests an extended move

## Next steps for a more serious version
1. Compare predictions against actual Kalshi settlements and report hit rate by time remaining.
2. Use the exact contract's official reference/settlement price rather than assuming another exchange's BTC price is identical.
3. Include Kalshi bid/ask spread, fees, liquidity, and implied probability in any decision rule.
4. Keep paper trading and add risk limits before considering order execution.
