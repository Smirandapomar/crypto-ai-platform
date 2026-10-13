import os
import time
import ccxt
import pandas as pd
from datetime import datetime, timezone

def fetch_ohlcv(symbol='ETH/USDT', timeframe='1h', limit=1000, days_back=90):
    print(f"--- Conectando a Binance para descargar {symbol} ({timeframe}) ---")
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })

    since = exchange.parse8601(
        (pd.Timestamp.now(tz=timezone.utc) - pd.Timedelta(days=days_back)).isoformat()
    )

    all_candles = []
    
    while True:
        try:
            candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
            if not candles:
                break
            
            all_candles.extend(candles)
            since = candles[-1][0] + 1
            
            if candles[-1][0] >= exchange.milliseconds() - 3600000:
                break

            time.sleep(exchange.rateLimit / 1000)
        except Exception as e:
            print(f"Error al descargar: {e}")
            break

    if not all_candles:
        print("No se encontraron datos.")
        return None

    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(all_candles, columns=columns)
    
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
    df.reset_index(drop=True, inplace=True)

    safe_symbol = symbol.replace('/', '_')
    filename = f"data/raw/{safe_symbol}_{timeframe}.csv"
    df.to_csv(filename, index=False)
    
    print(f"-> Descarga completada: {len(df)} registros.")
    print(f"-> Rango: {df['datetime'].iloc[0]} hasta {df['datetime'].iloc[-1]}")
    print(f"-> Archivo guardado en: {filename}")
    return df

if __name__ == '__main__':
    fetch_ohlcv(symbol='ETH/USDT', timeframe='1h', days_back=90)
