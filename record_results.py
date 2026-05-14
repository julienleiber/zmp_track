"""
record_results.py
Lance manuellement en fin de trimestre pour enregistrer la performance réalisée.

Usage :
    python3 record_results.py [--quarter 2026-Q1] [--dry-run]

Lit : quarters/YYYY-QN.json  (poids publiés en début de trimestre)
Écrit : track_record.csv     (ligne de résultats ajoutée)
Commit git automatique
"""

import argparse
import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

QUARTERS_DIR  = Path("quarters")
TRACK_RECORD  = Path("track_record.csv")
ASSET_COLS    = ["IEF", "TIP", "GLD", "FXY", "FXF", "LMT", "CVX", "SLV"]


def quarter_dates(quarter: str) -> tuple[str, str]:
    """Retourne (start, end) ISO d'un trimestre. Ex : 2026-Q1 → (2026-01-01, 2026-03-31)."""
    year, q = quarter.split("-Q")
    year = int(year)
    q    = int(q)
    starts = {1: "01-01", 2: "04-01", 3: "07-01", 4: "10-01"}
    ends   = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
    return f"{year}-{starts[q]}", f"{year}-{ends[q]}"


def current_quarter() -> str:
    now = datetime.today()
    q   = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{q}"


def fetch_returns(tickers: list, start: str, end: str) -> dict:
    """Rendement total sur la période pour chaque ticker."""
    end_fetch = str((pd.Timestamp(end) + pd.DateOffset(days=5)).date())
    rets = {}
    for t in tickers:
        raw = yf.download(t, start=start, end=end_fetch,
                          progress=False, auto_adjust=True)
        if raw.empty:
            rets[t] = None
            continue
        prices = raw["Close"].squeeze().dropna()
        # Premier prix disponible >= start, dernier prix <= end
        prices = prices[prices.index <= end]
        if len(prices) < 2:
            rets[t] = None
        else:
            rets[t] = float(prices.iloc[-1] / prices.iloc[0] - 1)
    return rets


def portfolio_return(weights: dict, asset_rets: dict) -> float | None:
    total = 0.0
    total_w = 0.0
    for t, w in weights.items():
        if t not in asset_rets or asset_rets[t] is None:
            continue
        total   += w * asset_rets[t]
        total_w += w
    if total_w < 0.8:
        return None
    return total / total_w


def format_pct(v) -> str:
    if v is None:
        return ""
    return f"{v*100:+.2f}%"


def git_commit(quarter: str):
    ts  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    msg = f"results: {quarter} — {ts}"
    subprocess.run(["git", "add", str(TRACK_RECORD)], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    print(f"  Commit : {msg}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quarter", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--notes", default="", help="Note optionnelle pour ce trimestre")
    args = parser.parse_args()

    quarter  = args.quarter or current_quarter()
    q_path   = QUARTERS_DIR / f"{quarter}.json"

    if not q_path.exists():
        print(f"ERREUR : {q_path} introuvable. Lancer d'abord publish_quarterly.py.")
        raise SystemExit(1)

    with open(q_path) as f:
        pub = json.load(f)

    weights       = pub["weights"]
    signal        = pub["signal"]
    date_published = pub["date_published"]

    start, end = quarter_dates(quarter)
    print(f"\n=== Record {quarter} | {start} → {end} ===")
    print(f"  Signal publié : {signal} le {date_published}")

    # Téléchargement des performances
    print("  Téléchargement des rendements...")
    all_tickers = ASSET_COLS + ["SPY", "AGG"]
    rets = fetch_returns(all_tickers, start, end)

    zmp_ret  = portfolio_return(weights, rets)
    spy_ret  = rets.get("SPY")
    agg_ret  = rets.get("AGG")
    r6040    = (0.6 * spy_ret + 0.4 * agg_ret) if (spy_ret and agg_ret) else None

    print(f"  ZMP   : {format_pct(zmp_ret)}")
    print(f"  SPY   : {format_pct(spy_ret)}")
    print(f"  60/40 : {format_pct(r6040)}")

    row = {
        "date_published": date_published,
        "quarter":        quarter,
        "signal":         signal,
        **{t: weights.get(t, 0.0) for t in ASSET_COLS},
        "zmp_return":     format_pct(zmp_ret),
        "spy_return":     format_pct(spy_ret),
        "r6040_return":   format_pct(r6040),
        "notes":          args.notes,
    }

    if not args.dry_run:
        fieldnames = (["date_published", "quarter", "signal"] +
                      ASSET_COLS +
                      ["zmp_return", "spy_return", "r6040_return", "notes"])
        write_header = not TRACK_RECORD.exists()
        with open(TRACK_RECORD, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        print(f"  Ligne ajoutée dans {TRACK_RECORD}")
        git_commit(quarter)
    else:
        print("\n  [dry-run] ligne qui serait ajoutée :")
        print(f"  {row}")


if __name__ == "__main__":
    main()
