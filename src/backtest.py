import joblib
import pandas as pd
import numpy as np

def run_backtest(
    features_path='data/processed/ETH_USDT_features.csv',
    model_path='models/rf_eth_model.pkl',
    initial_capital=1000.0,
    min_confidence=0.55,    # Exigir al menos 55% de convicción a la IA
    fee=0.001               # 0.1% de comisión de exchange
):
    df = pd.read_csv(features_path)
    model = joblib.load(model_path)

    feature_cols = [
        'log_return', 'atr_pct', 'rsi', 'macd_diff', 
        'ema_cross', 'volume_surge'
    ]

    split_index = int(len(df) * 0.8)
    test_df = df.iloc[split_index:].copy().reset_index(drop=True)
    test_df['buy_proba'] = model.predict_proba(test_df[feature_cols])[:, 1]

    capital = initial_capital
    in_position = False
    entry_price = 0.0
    stop_loss_price = 0.0
    take_profit_price = 0.0
    trades = []

    for i in range(len(test_df) - 1):
        row = test_df.iloc[i]
        current_price = row['close']
        next_open = test_df.iloc[i + 1]['open']
        atr_val = row['atr']
        proba = row['buy_proba']
        ema_c = row['ema_cross']
        time = row['datetime']

        if in_position:
            # Salida dinámica por Stop Loss o Take Profit
            if current_price <= stop_loss_price:
                price_change = (stop_loss_price - entry_price) / entry_price
                capital = capital * (1 + price_change) * (1 - fee)
                in_position = False
                trades.append({'type': 'STOP_LOSS', 'pnl_pct': price_change * 100})

            elif current_price >= take_profit_price:
                price_change = (take_profit_price - entry_price) / entry_price
                capital = capital * (1 + price_change) * (1 - fee)
                in_position = False
                trades.append({'type': 'TAKE_PROFIT', 'pnl_pct': price_change * 100})

        elif not in_position:
            # Entrada: Probabilidad de IA suficiente + cruce de medias a favor
            if proba >= min_confidence and ema_c > 0:
                in_position = True
                entry_price = next_open
                capital = capital * (1 - fee)
                
                # Stop dinámico por volatilidad (1.5x ATR) y Take Profit (3x ATR)
                stop_loss_price = entry_price - (1.5 * atr_val)
                take_profit_price = entry_price + (3.0 * atr_val)
                trades.append({'type': 'COMPRA', 'entry_time': time})

    if in_position:
        final_price = test_df.iloc[-1]['close']
        price_change = (final_price - entry_price) / entry_price
        capital = capital * (1 + price_change) * (1 - fee)
        trades.append({'type': 'CIERRE_FINAL', 'pnl_pct': price_change * 100})

    bnh_return = ((test_df.iloc[-1]['close'] - test_df.iloc[0]['open']) / test_df.iloc[0]['open']) * 100
    strat_return = ((capital - initial_capital) / initial_capital) * 100

    closed = [t for t in trades if 'pnl_pct' in t]
    wins = [t for t in closed if t['pnl_pct'] > 0]
    win_rate = (len(wins) / len(closed) * 100) if closed else 0

    print("\n================ BACKTEST CON GESTIÓN DINÁMICA ATR ================")
    print(f"Capital Inicial:             USD")
    print(f"Capital Final con IA:        USD")
    print(f"Rentabilidad Estrategia:    {strat_return:+.2f}%")
    print(f"Rentabilidad Buy & Hold:    {bnh_return:+.2f}%")
    print(f"Total operaciones cerradas: {len(closed)}")
    print(f"Operaciones ganadoras:      {len(wins)}")
    print(f"Tasa de Acierto (Win Rate): {win_rate:.2f}%")
    print("===================================================================\n")

if __name__ == '__main__':
    run_backtest()
