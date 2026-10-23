import os, time, threading
from datetime import datetime, timezone
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "kalshi-btc-signal-dashboard/1.0"})
KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
BINANCE_BASE = "https://api.binance.com/api/v3"
SERIES = os.getenv("KALSHI_SERIES", "KXBTC15M")

HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#10131b">
<title>BTC 15m Signal</title>
<style>
:root{color-scheme:dark;--bg:#10131b;--card:#191e2a;--muted:#9ba6b8;--line:#2c3445;--white:#f6f8fc}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--white);font:16px -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}
main{max-width:720px;margin:auto;padding:20px 14px 40px}.eyebrow{color:#9ba6b8;font-size:12px;letter-spacing:.12em;text-transform:uppercase}
h1{font-size:26px;margin:7px 0 4px}.sub{color:var(--muted);font-size:14px;line-height:1.45}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;min-width:0}
.label{color:var(--muted);font-size:12px;margin-bottom:8px}.value{font-size:24px;font-weight:750;overflow-wrap:anywhere}.small{font-size:13px;color:var(--muted);line-height:1.5;margin-top:8px}
.signal{margin-top:12px;padding:22px 16px;text-align:center;border-radius:18px;background:#202635;border:1px solid var(--line)}
.signal .value{font-size:36px;letter-spacing:.02em}.up{color:#5ee0a0}.down{color:#ff8585}.neutral{color:#ffd27b}
section{margin-top:12px}.row{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}.row:last-child{border:0}
button{width:100%;padding:13px;border:1px solid var(--line);border-radius:12px;background:#242c3b;color:var(--white);font-size:15px;font-weight:650;margin-top:14px}
footer{margin-top:18px;color:var(--muted);font-size:12px;line-height:1.55}
@media(max-width:360px){.grid{grid-template-columns:1fr}.value{font-size:22px}}
</style>
</head>
<body><main>
<div class="eyebrow">Live market monitor · signal only</div>
<h1>BTC 15-minute signal</h1>
<div class="sub">Keep this page open for live refreshes. Place any bets manually on your computer.</div>
<div class="signal" id="signalBox"><div class="label">CURRENT INDICATOR</div><div class="value neutral" id="signal">CONNECTING…</div><div class="small" id="reason">Waiting for market data</div></div>
<div class="grid">
 <div class="card"><div class="label">BTC spot price (BTC/USDT)</div><div class="value" id="price">—</div><div class="small" id="feed">Loading feed…</div></div>
 <div class="card"><div class="label">Time left in Kalshi market</div><div class="value" id="remaining">—</div><div class="small" id="ticker">Finding active market…</div></div>
 <div class="card"><div class="label">Indicator score</div><div class="value" id="score">—</div><div class="small">Scale −3 to +3; not a probability</div></div>
 <div class="card"><div class="label">RSI (14)</div><div class="value" id="rsi">—</div><div class="small" id="momentum">Momentum: —</div></div>
</div>
<section class="card">
<div class="label">Market details</div>
<div class="row"><span>Contract</span><strong id="title">—</strong></div>
<div class="row"><span>YES bid / ask</span><strong id="quotes">—</strong></div>
<div class="row"><span>Data updated</span><strong id="updated">—</strong></div>
<div class="row"><span>Service status</span><strong id="status">Loading…</strong></div>
<button onclick="refresh()">Refresh now</button>
</section>
<footer>
Experimental technical indicator only. It is not a validated prediction or a guarantee. BTC/USDT may differ from the precise reference price used to settle a Kalshi contract. Check the contract's rules and compare price, strike, spread, liquidity, and time remaining yourself. This dashboard never places orders. Do not rely on stale or missing data.
</footer>
</main>
<script>
function fmtMoney(n){return n==null?'—':Number(n).toLocaleString('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2})}
function fmtCents(n){return n==null?'—':n+'¢'}
async function refresh(){
 try{
  const r=await fetch('/api/signal',{cache:'no-store'}); const d=await r.json();
  document.getElementById('price').textContent=fmtMoney(d.btc_price);
  document.getElementById('feed').textContent=d.feed_age_seconds==null?'Feed age unavailable':`Feed update ${d.feed_age_seconds}s ago`;
  document.getElementById('remaining').textContent=d.market?.seconds_remaining==null?'—':`${Math.floor(d.market.seconds_remaining/60)}m ${d.market.seconds_remaining%60}s`;
  document.getElementById('ticker').textContent=d.market?.ticker||'Active contract not confirmed';
  document.getElementById('title').textContent=d.market?.title||'Not found';
  document.getElementById('quotes').textContent=d.market?`${fmtCents(d.market.yes_bid)} / ${fmtCents(d.market.yes_ask)}`:'—';
  document.getElementById('score').textContent=d.score==null?'—':`${d.score>0?'+':''}${d.score}`;
  document.getElementById('rsi').textContent=d.rsi==null?'—':Number(d.rsi).toFixed(1);
  document.getElementById('momentum').textContent=d.momentum_1m==null?'Momentum unavailable':`1m ${d.momentum_1m.toFixed(3)}% · 5m ${d.momentum_5m.toFixed(3)}%`;
  document.getElementById('reason').textContent=d.reason||'No explanation';
  document.getElementById('updated').textContent=new Date().toLocaleTimeString();
  document.getElementById('status').textContent=d.status||'Unknown';
  const sig=document.getElementById('signal'); sig.textContent=d.signal||'NO TRADE';
  sig.className='value '+(d.signal==='UP'?'up':d.signal==='DOWN'?'down':'neutral');
 }catch(e){document.getElementById('status').textContent='Connection issue';}
}
refresh(); setInterval(refresh,5000);
</script></body></html>
"""

def utc_now():
    return datetime.now(timezone.utc)

def get_candles():
    r = SESSION.get(f"{BINANCE_BASE}/klines", params={"symbol":"BTCUSDT","interval":"1m","limit":100}, timeout=8)
    r.raise_for_status()
    data = r.json()
    return [{"time": int(x[0] / 1000), "open": float(x[1]), "high": float(x[2]), "low": float(x[3]), "close": float(x[4]), "volume": float(x[5])} for x in data]

def get_market():
    r = SESSION.get(f"{KALSHI_BASE}/markets", params={"series_ticker":SERIES,"status":"open","limit":200}, timeout=8)
    r.raise_for_status()
    markets = r.json().get("markets", [])
    now = utc_now()
    eligible = []
    for m in markets:
        stamp = m.get("close_time") or m.get("expiration_time")
        if stamp:
            try:
                dt = datetime.fromisoformat(stamp.replace("Z","+00:00"))
                if dt > now: eligible.append((dt,m))
            except ValueError:
                pass
    if not eligible: return None
    eligible.sort(key=lambda z:z[0])
    close_dt, m = eligible[0]
    return {"ticker":m.get("ticker"),"title":m.get("title"),"yes_bid":m.get("yes_bid"),"yes_ask":m.get("yes_ask"),"seconds_remaining":max(0,int((close_dt-now).total_seconds()))}

def ema(values, period):
    if len(values)<period: return None
    a=2/(period+1); v=values[0]
    for x in values[1:]: v=a*x+(1-a)*v
    return v

def get_rsi(values, period=14):
    if len(values)<period+1: return None
    changes=[values[i]-values[i-1] for i in range(1,len(values))]
    gains=sum(max(x,0) for x in changes[-period:])/period
    losses=sum(max(-x,0) for x in changes[-period:])/period
    if losses==0: return 100.0 if gains>0 else 50.0
    rs=gains/losses
    return 100-(100/(1+rs))

def build_signal():
    out={"signal":"NO TRADE","score":0,"reason":"Waiting for data","status":"OK"}
    try:
        candles=get_candles()
        closes=[c["close"] for c in candles]
        out["btc_price"]=closes[-1]
        out["feed_age_seconds"]=max(0,int(time.time()-candles[-1]["time"]))
        if len(closes)<20:
            out["reason"]="Not enough candles yet"; return out
        fast=ema(closes[-40:],5); slow=ema(closes[-60:],13)
        m1=(closes[-1]/closes[-2]-1)*100
        m5=(closes[-1]/closes[-6]-1)*100
        rv=get_rsi(closes)
        score=0; why=[]
        if fast>slow: score+=1; why.append("fast EMA above slow EMA")
        elif fast<slow: score-=1; why.append("fast EMA below slow EMA")
        if m1>0.015: score+=1; why.append("positive 1m momentum")
        elif m1<-.015: score-=1; why.append("negative 1m momentum")
        if m5>0.04: score+=1; why.append("positive 5m momentum")
        elif m5<-.04: score-=1; why.append("negative 5m momentum")
        out.update({"score":score,"rsi":rv,"momentum_1m":m1,"momentum_5m":m5})
        if (rv>=78 and score>0) or (rv<=22 and score<0):
            out["reason"]=f"RSI extreme ({rv:.1f}); avoid chasing"
        elif score>=2: out["signal"]="UP"; out["reason"]="; ".join(why)
        elif score<=-2: out["signal"]="DOWN"; out["reason"]="; ".join(why)
        else: out["reason"]="Indicators disagree or are too weak"
        if out["feed_age_seconds"]>90:
            out["signal"]="NO TRADE"; out["reason"]="Price feed is stale"
            out["status"]="STALE PRICE FEED"
    except Exception as e:
        out["status"]="DATA ERROR"
        out["reason"]=f"Could not retrieve price data: {type(e).__name__}"
    try:
        out["market"]=get_market()
    except Exception:
        out["market"]=None
        out["status"]="KALSHI MARKET UNAVAILABLE"
    out["server_time"]=utc_now().isoformat()
    return out

@app.get("/")
def home():
    return render_template_string(HTML)

@app.get("/api/signal")
def api_signal():
    return jsonify(build_signal())

@app.get("/health")
def health():
    return jsonify({"ok":True,"time":utc_now().isoformat()})

if __name__ == "__main__":
    port=int(os.getenv("PORT","8080"))
    app.run(host="0.0.0.0",port=port)
