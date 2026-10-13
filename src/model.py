import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def train_model(input_path='data/processed/ETH_USDT_features.csv', model_output='models/rf_eth_model.pkl'):
    df = pd.read_csv(input_path)

    feature_cols = [
        'log_return', 'atr_pct', 'rsi', 'macd_diff', 
        'ema_cross', 'volume_surge'
    ]
    
    X = df[feature_cols]
    y = df['target']

    split_index = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    # Ajustamos class_weight='balanced_subsample' para forzarlo a detectar subidas
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        min_samples_leaf=5,
        class_weight='balanced_subsample',
        random_state=42
    )

    print("--- Reentrenando Modelo Calibrado ---")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\n--- Métricas de Test (Umbral 50%) ---")
    print(classification_report(y_test, y_pred, target_names=['Esperar (0)', 'Comprar (1)'], zero_division=0))

    joblib.dump(model, model_output)
    print(f"-> Modelo guardado en: {model_output}")

if __name__ == '__main__':
    train_model()
