import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import AverageTrueRange

def create_features(input_path='data/raw/ETH_USDT_1h.csv', output_path='data/processed/ETH_USDT_features.csv'):
    print(f"--- Enriqueciendo datos con Volatilidad y Volumen ---")
    df = pd.read_csv(input_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.sort_values('datetime', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 1. Retornos y Volatilidad
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['atr'] = atr.average_true_range()
    df['atr_pct'] = df['atr'] / df['close']

    # 2. Indicadores de Impulso y Tendencia
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()

    macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['macd_diff'] = macd.macd_diff()

    df['ema_9'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
    df['ema_21'] = EMAIndicator(close=df['close'], window=21).ema_indicator()
    df['ema_cross'] = (df['ema_9'] - df['ema_21']) / df['close']

    # 3. Analisis de Volumen
    df['vol_sma_20'] = df['volume'].rolling(window=20).mean()
    df['volume_surge'] = df['volume'] / df['vol_sma_20']

    # 4. Target a 6 horas (subida > 1.2%)
    horizon = 6
    df['future_return'] = (df['close'].shift(-horizon) - df['close']) / df['close']
    df['target'] = (df['future_return'] > 0.012).astype(int)

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    df.to_csv(output_path, index=False)
    print(f"-> Nuevas features guardadas exitosamente: {len(df)} filas.")
    print(df['target'].value_counts(normalize=True))

if __name__ == '__main__':
    create_features()
