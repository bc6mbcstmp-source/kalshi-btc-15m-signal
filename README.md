# Kalshi BTC 15-minute signal dashboard (iPhone setup)

This project gives you a mobile-friendly dashboard. It uses public BTC/USDT 1-minute candles and polls Kalshi's public market endpoint for a currently open `KXBTC15M` series contract. It only displays signals; it does not submit trades.

## Deploy from iPhone using GitHub + Render

1. In Safari, sign in to GitHub or create an account.
2. Create a new **public** repository named `kalshi-btc-15m-signal`. (Public is easiest for a basic free deployment; this code contains no secrets.)
3. Upload these three files at the repository root: `app.py`, `requirements.txt`, and `render.yaml`. You can use GitHub's web interface to add each file.
4. Sign in to Render in Safari and choose **New → Blueprint** (or deploy a new web service from the GitHub repository, if Blueprint is not shown).
5. Connect `kalshi-btc-15m-signal` and approve deployment. Render reads `render.yaml`, installs dependencies, and starts the dashboard.
6. When deployment finishes, open the Render-provided `https://...onrender.com` URL on your iPhone. Save it to the Home Screen using Safari's Share → Add to Home Screen.
7. Keep your Kalshi market open on your computer and use the phone dashboard as a separate signal monitor.

## Important
- Render's free service may sleep when idle and take time to wake. Free-tier features/pricing can change; check Render's current plan details before relying on it.
- The app fetches public data when the dashboard refreshes every five seconds; a server may be throttled by upstream APIs.
- It defaults to series ticker `KXBTC15M`. If no active market appears, verify the current series/market ticker in Kalshi's public API or market UI; do not assume the contract was found.
- The BTC/USDT market feed may not match the exact settlement reference used by the Kalshi contract.
- Signal score (−3 to +3) is a rule-based indicator, not a calibrated probability or guarantee. It has not been backtested.
- This version has no order execution, no API keys, and no account connection.
- Check the market's exact rules, reference price, closing time, fees, spread, and liquidity before making any manual trade.
