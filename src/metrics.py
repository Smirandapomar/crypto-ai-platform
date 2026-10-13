import numpy as np
import pandas as pd

def calculate_advanced_metrics(equity_curve: list, risk_free_rate: float = 0.04):
    """
    Calcula Sharpe, Sortino y Maximum Drawdown a partir de la curva de capital.
    risk_free_rate: Tasa libre de riesgo anualizada (ej. 4% anual = 0.04).
    """
    if len(equity_curve) < 2:
        return {"sharpe": 0.0, "sortino": 0.0, "max_drawdown": 0.0}

    series = pd.Series(equity_curve)
    returns = series.pct_change().dropna()

    if len(returns) == 0 or returns.std() == 0:
        return {"sharpe": 0.0, "sortino": 0.0, "max_drawdown": 0.0}

    # Asumiendo velas de 1h (8,760 periodos anuales)
    periods_per_year = 8760
    rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1

    excess_returns = returns - rf_per_period
    mean_excess = excess_returns.mean()
    std_dev = returns.std()

    # 1. Sharpe Ratio Anualizado
    sharpe = (mean_excess / std_dev) * np.sqrt(periods_per_year) if std_dev > 0 else 0.0

    # 2. Sortino Ratio (solo volatilidad negativa)
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std() if len(downside_returns) > 0 else 0.0
    sortino = (mean_excess / downside_std) * np.sqrt(periods_per_year) if downside_std > 0 else 0.0

    # 3. Maximum Drawdown (Max DD)
    cumulative_max = series.cummax()
    drawdowns = (series - cumulative_max) / cumulative_max
    max_dd = drawdowns.min() * 100 # en porcentaje

    return {
        "sharpe": round(float(sharpe), 2),
        "sortino": round(float(sortino), 2),
        "max_drawdown": round(float(max_dd), 2)
    }

if __name__ == '__main__':
    # Prueba unitaria
    ejemplo_curva = [1000, 1020, 1015, 1040, 1030, 1082.4]
    m = calculate_advanced_metrics(ejemplo_curva)
    print("Métricas de prueba:", m)
