"""
publish_quarterly.py
Lance manuellement au début de chaque trimestre.

Usage :
    python3 publish_quarterly.py [--quarter 2026-Q2] [--dry-run]

Sorties :
    quarters/YYYY-QN.json   — signal + poids + date de publication
    Commit git automatique horodaté
"""

import argparse
import json
import subprocess
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

warnings.filterwarnings("ignore")

# ─── Configuration ─────────────────────────────────────────────────────────────

RESISTANTS          = ["IEF", "TIP", "GLD", "FXY", "FXF"]
AMPLIFIERS          = ["LMT", "CVX", "SLV"]
ALL_ASSETS          = RESISTANTS + AMPLIFIERS
FX_PROTECTION_ONLY  = ["FXY", "FXF"]

W_MAX               = 0.25
W_MIN               = 0.00
R_MIN_EXPANSION     = 0.50
R_MAX_EXPANSION     = 0.60
R_MIN_PROTECTION    = 0.70
R_MAX_PROTECTION    = 0.80
RF_ANNUAL           = 0.03
LOOKBACK_MONTHS     = 36
QUARTERS_DIR        = Path("quarters")
SIGNAL_PATH         = Path("signal_current.json")

# ─── Chargement des données ────────────────────────────────────────────────────

def load_prices(months: int = LOOKBACK_MONTHS) -> pd.DataFrame:
    end   = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(months=months + 2)
    frames = {}
    for t in ALL_ASSETS + ["SPY", "AGG"]:
        raw = yf.download(t, start=str(start.date()), end=str(end.date()),
                          progress=False, auto_adjust=True)
        if not raw.empty:
            s = raw["Close"].squeeze().dropna()
            frames[t] = s.resample("ME").last()
    df = pd.DataFrame(frames).dropna(how="all")
    return df.tail(months)


# ─── Optimisation ──────────────────────────────────────────────────────────────

def optimize_expansion(returns: pd.DataFrame) -> dict:
    rf  = RF_ANNUAL / 12
    tickers = list(returns.columns)
    n   = len(tickers)
    r_idx  = [i for i, t in enumerate(tickers) if t in RESISTANTS]
    fx_idx = [i for i, t in enumerate(tickers) if t in FX_PROTECTION_ONLY]
    mu  = returns.mean().values
    cov = returns.cov().values

    def neg_sharpe(w):
        pr = w @ mu - rf
        pv = np.sqrt(w @ cov @ w)
        return -pr / (pv + 1e-10)

    constraints = [
        {"type": "eq",   "fun": lambda w: w.sum() - 1},
        {"type": "ineq", "fun": lambda w: w[r_idx].sum() - R_MIN_EXPANSION},
        {"type": "ineq", "fun": lambda w: R_MAX_EXPANSION - w[r_idx].sum()},
    ]
    bounds = [(0.0, 0.0) if i in fx_idx else (W_MIN, W_MAX) for i in range(n)]
    res = minimize(neg_sharpe, np.ones(n) / n, method="SLSQP",
                   bounds=bounds, constraints=constraints,
                   options={"maxiter": 2000, "ftol": 1e-9})
    w = np.maximum(res.x, 0)
    return dict(zip(tickers, (w / w.sum()).round(4)))


def optimize_protection(returns: pd.DataFrame) -> dict:
    rf  = RF_ANNUAL / 12
    tickers = list(returns.columns)
    n   = len(tickers)
    r_idx = [i for i, t in enumerate(tickers) if t in RESISTANTS]
    mu  = returns.mean().values
    cov = returns.cov().values

    def neg_sharpe(w):
        pr = w @ mu - rf
        pv = np.sqrt(w @ cov @ w)
        return -pr / (pv + 1e-10)

    constraints = [
        {"type": "eq",   "fun": lambda w: w.sum() - 1},
        {"type": "ineq", "fun": lambda w: w[r_idx].sum() - R_MIN_PROTECTION},
        {"type": "ineq", "fun": lambda w: R_MAX_PROTECTION - w[r_idx].sum()},
    ]
    bounds = [(W_MIN, W_MAX)] * n
    res = minimize(neg_sharpe, np.ones(n) / n, method="SLSQP",
                   bounds=bounds, constraints=constraints,
                   options={"maxiter": 2000, "ftol": 1e-9})
    w = np.maximum(res.x, 0)
    return dict(zip(tickers, (w / w.sum()).round(4)))


# ─── Main ──────────────────────────────────────────────────────────────────────

def current_quarter() -> str:
    now = datetime.today()
    q   = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{q}"


def git_commit(quarter: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    msg = f"publish: {quarter} — {ts}"
    subprocess.run(["git", "add", f"quarters/{quarter}.json"], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    print(f"  Commit : {msg}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quarter", default=None,
                        help="Ex: 2026-Q2 (défaut : trimestre courant)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Calcule sans écrire ni commiter")
    args = parser.parse_args()

    quarter = args.quarter or current_quarter()
    out_path = QUARTERS_DIR / f"{quarter}.json"
    QUARTERS_DIR.mkdir(exist_ok=True)

    # Signal courant
    if SIGNAL_PATH.exists():
        with open(SIGNAL_PATH) as f:
            sig_data = json.load(f)
        signal    = sig_data["signal"]
        baa_aaa   = sig_data.get("baa_aaa")
        gli_yoy   = sig_data.get("gli_yoy")
        gli_decel = sig_data.get("gli_decel")
    else:
        signal, baa_aaa, gli_yoy, gli_decel = "Expansion", None, None, None
        print("  ⚠ signal_current.json absent — signal par défaut : Expansion")

    print(f"\n=== Publish {quarter} | Signal : {signal} ===")

    # Prix et rendements
    print("  Téléchargement des prix (36 mois)...")
    prices  = load_prices()
    rets    = prices[ALL_ASSETS].pct_change().dropna()

    # Optimisation
    if signal == "Protection":
        weights = optimize_protection(rets)
    else:
        weights = optimize_expansion(rets)

    # Sortie
    payload = {
        "quarter":          quarter,
        "date_published":   datetime.utcnow().strftime("%Y-%m-%d"),
        "signal":           signal,
        "baa_aaa":          baa_aaa,
        "gli_yoy":          gli_yoy,
        "gli_decel":        gli_decel,
        "lookback_months":  LOOKBACK_MONTHS,
        "weights":          weights,
    }

    print("\n  Poids optimisés :")
    for t, w in weights.items():
        if t in ALL_ASSETS:
            print(f"    {t:<6} {w*100:5.1f}%")

    if not args.dry_run:
        with open(out_path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"\n  Écrit : {out_path}")
        git_commit(quarter)
    else:
        print("\n  [dry-run] aucun fichier écrit")


if __name__ == "__main__":
    main()
