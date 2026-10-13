import os
import joblib
import ccxt
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import AverageTrueRange

app = FastAPI(title="Crypto AI Trading Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "models/rf_eth_model.pkl"
model = joblib.load(MODEL_PATH)

feature_cols = [
    'log_return', 'atr_pct', 'rsi', 'macd_diff', 
    'ema_cross', 'volume_surge'
]

def get_fallback_candles():
    try:
        df = pd.read_csv('data/processed/ETH_USDT_features.csv')
        candles = []
        for _, r in df.tail(100).iterrows():
            candles.append({
                "time": int(pd.to_datetime(r['datetime']).timestamp()),
                "open": float(r['close']),
                "high": float(r['close'] * 1.002),
                "low": float(r['close'] * 0.998),
                "close": float(r['close'])
            })
        return candles
    except Exception:
        return []

@app.get("/api/health")
def health_check():
    return {"status": "ok", "model_loaded": True}

@app.get("/api/candles")
def get_candles(symbol: str = "ETH/USDT", limit: int = 100):
    try:
        exchange = ccxt.binance({'enableRateLimit': True, 'timeout': 3500})
        candles = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=limit)
        chart_data = []
        for c in candles:
            chart_data.append({
                "time": int(c[0] / 1000),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4])
            })
        return chart_data
    except Exception as e:
        print(f"Aviso: Binance API demoró ({e}), usando velas procesadas locales.")
        return get_fallback_candles()

@app.get("/api/live-signal")
def get_live_signal(symbol: str = "ETH/USDT"):
    try:
        exchange = ccxt.binance({'enableRateLimit': True, 'timeout': 3500})
        candles = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=60)
        
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(candles, columns=columns)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
        df['atr'] = atr.average_true_range()
        df['atr_pct'] = df['atr'] / df['close']

        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd_diff'] = macd.macd_diff()

        df['ema_9'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_21'] = EMAIndicator(close=df['close'], window=21).ema_indicator()
        df['ema_cross'] = (df['ema_9'] - df['ema_21']) / df['close']

        df['vol_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_surge'] = df['volume'] / df['vol_sma_20']

        latest = df.iloc[-1]
        features_vector = latest[feature_cols].to_frame().T

        proba = float(model.predict_proba(features_vector)[0][1])
        ema_c = float(latest['ema_cross'])
        last_price = float(latest['close'])
        rsi_val = round(float(latest['rsi']), 2)
        atr_val = round(float(latest['atr_pct']) * 100, 2)
        ts_str = str(latest['datetime'])
    except Exception as e:
        print(f"Aviso: Usando inferencia local ({e})")
        df_local = pd.read_csv('data/processed/ETH_USDT_features.csv')
        latest = df_local.iloc[-1]
        features_vector = latest[feature_cols].to_frame().T
        proba = float(model.predict_proba(features_vector)[0][1])
        ema_c = float(latest['ema_cross'])
        last_price = float(latest['close'])
        rsi_val = round(float(latest['rsi']), 2)
        atr_val = round(float(latest['atr_pct']) * 100, 2)
        ts_str = str(latest['datetime'])

    signal = "ESPERAR / NEUTRAL"
    recommendation = "El mercado no presenta condiciones cuantitativas de entrada con alta probabilidad."
    
    if proba >= 0.55 and ema_c > 0:
        signal = "COMPRA"
        recommendation = "Cruce alcista de medias respaldado por alta convicción del modelo de Machine Learning."

    return {
        "symbol": symbol,
        "last_price": last_price,
        "timestamp": ts_str,
        "confidence": round(proba * 100, 2),
        "signal": signal,
        "recommendation": recommendation,
        "indicators": {
            "rsi": rsi_val,
            "atr_pct": atr_val,
            "ema_cross": round(ema_c, 5)
        }
    }

class SimulationRequest(BaseModel):
    initial_capital: float = 1000.0

@app.post("/api/simulate")
def simulate(req: SimulationRequest):
    try:
        features_path = 'data/processed/ETH_USDT_features.csv'
        df = pd.read_csv(features_path)
        split_index = int(len(df) * 0.8)
        test_df = df.iloc[split_index:].copy().reset_index(drop=True)
        test_df['buy_proba'] = model.predict_proba(test_df[feature_cols])[:, 1]

        capital = req.initial_capital
        in_position = False
        entry_price = 0.0
        stop_loss_price = 0.0
        take_profit_price = 0.0
        trades_count = 0
        winning_trades = 0

        for i in range(len(test_df) - 1):
            row = test_df.iloc[i]
            current_price = row['close']
            next_open = test_df.iloc[i + 1]['open']
            atr_val = row['atr']
            proba = row['buy_proba']
            ema_c = row['ema_cross']

            if in_position:
                if current_price <= stop_loss_price:
                    chg = (stop_loss_price - entry_price) / entry_price
                    capital = capital * (1 + chg) * 0.999
                    in_position = False
                    trades_count += 1
                    if chg > 0: winning_trades += 1
                elif current_price >= take_profit_price:
                    chg = (take_profit_price - entry_price) / entry_price
                    capital = capital * (1 + chg) * 0.999
                    in_position = False
                    trades_count += 1
                    if chg > 0: winning_trades += 1
            elif not in_position and proba >= 0.55 and ema_c > 0:
                in_position = True
                entry_price = next_open
                capital = capital * 0.999
                stop_loss_price = entry_price - (1.5 * atr_val)
                take_profit_price = entry_price + (3.0 * atr_val)

        return {
            "initial_capital": req.initial_capital,
            "final_capital": round(capital, 2),
            "net_profit_pct": round(((capital - req.initial_capital) / req.initial_capital) * 100, 2),
            "total_trades": trades_count,
            "win_rate": round((winning_trades / trades_count * 100) if trades_count > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

os.makedirs("frontend", exist_ok=True)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
