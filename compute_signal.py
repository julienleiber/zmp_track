"""
compute_signal.py
Calcule le signal quotidien ZMP et met à jour signal_current.json.
Lancé par GitHub Actions chaque jour à 18h00 UTC.

Signal :
  Protection si BAA−AAA > 1.30 ET GLI YoY décélère (diff 3 mois < 0)
  Sortie    : BAA−AAA < 1.15 (hystérésis)
  Expansion sinon
"""

import json
import os
import sys
import requests
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

FRED_KEY      = os.environ["FRED_API_KEY"]
FRED_BASE     = "https://api.stlouisfed.org/fred/series/observations"
BAA_THRESHOLD = 1.30
BAA_EXIT      = 1.15
GLI_PATH      = Path("data/gli_current.json")
SIGNAL_PATH   = Path("signal_current.json")


def fetch_fred(series_id: str, limit: int = 10) -> pd.Series:
    """Récupère les N dernières observations d'une série FRED."""
    r = requests.get(
        FRED_BASE,
        params={
            "series_id":      series_id,
            "api_key":        FRED_KEY,
            "file_type":      "json",
            "sort_order":     "desc",
            "limit":          limit,
            "observation_start": "2020-01-01",
        },
        timeout=30,
    )
    r.raise_for_status()
    obs = r.json()["observations"]
    s = pd.Series(
        {o["date"]: float(o["value"]) for o in obs if o["value"] != "."},
        dtype=float,
    )
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def get_baa_aaa_spread() -> tuple[float, str]:
    """Retourne (spread_du_jour, date_ISO)."""
    dbaa = fetch_fred("DBAA", limit=5)
    daaa = fetch_fred("DAAA", limit=5)
    common = dbaa.index.intersection(daaa.index)
    spread = (dbaa - daaa).loc[common]
    latest_date  = spread.index[-1]
    latest_value = spread.iloc[-1]
    return float(latest_value), str(latest_date.date())


def get_gli_decel() -> tuple[bool, float, float]:
    """
    Retourne (gli_decel, gli_yoy_current, gli_yoy_3m_ago).
    Lit data/gli_current.json mis à jour manuellement chaque trimestre.
    """
    if not GLI_PATH.exists():
        print("  ⚠ gli_current.json absent — GLI décélération supposée false")
        return False, float("nan"), float("nan")

    with open(GLI_PATH) as f:
        data = json.load(f)

    entries = sorted(data["observations"], key=lambda x: x["date"])
    if len(entries) < 5:
        return False, float("nan"), float("nan")

    # YoY (4 trimestres)
    dates  = [e["date"] for e in entries]
    levels = [e["gli_level"] for e in entries]
    s = pd.Series(levels, index=pd.to_datetime(dates))
    yoy = s.pct_change(4) * 100

    current_yoy = float(yoy.iloc[-1])
    prev_yoy    = float(yoy.iloc[-2])  # trimestre précédent
    decel       = (current_yoy - prev_yoy) < 0
    return decel, current_yoy, prev_yoy


def load_previous_signal() -> str:
    if SIGNAL_PATH.exists():
        with open(SIGNAL_PATH) as f:
            return json.load(f).get("signal", "Expansion")
    return "Expansion"


def compute_signal(spread: float, prev_signal: str, gli_decel: bool) -> str:
    """Applique la logique hystérésis du signal."""
    if prev_signal == "Protection":
        if spread < BAA_EXIT:
            return "Expansion"
        return "Protection"
    else:
        if spread > BAA_THRESHOLD and gli_decel:
            return "Protection"
        return "Expansion"


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Calcul du signal...")

    try:
        spread, spread_date = get_baa_aaa_spread()
        print(f"  BAA−AAA spread : {spread:.4f} ({spread_date})")
    except Exception as e:
        print(f"  ERREUR FRED : {e}")
        sys.exit(1)

    gli_decel, gli_yoy, gli_yoy_prev = get_gli_decel()
    print(f"  GLI YoY        : {gli_yoy:.2f}% (prev {gli_yoy_prev:.2f}%) → decel={gli_decel}")

    prev_signal = load_previous_signal()
    signal      = compute_signal(spread, prev_signal, gli_decel)
    print(f"  Signal         : {prev_signal} → {signal}")

    payload = {
        "date":        spread_date,
        "generated":   datetime.now(timezone.utc).isoformat(),
        "signal":      signal,
        "baa_aaa":     round(spread, 4),
        "baa_date":    spread_date,
        "gli_yoy":     round(gli_yoy, 4) if gli_yoy == gli_yoy else None,
        "gli_decel":   gli_decel,
        "threshold":   BAA_THRESHOLD,
        "exit":        BAA_EXIT,
    }

    with open(SIGNAL_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Écrit : {SIGNAL_PATH}")


if __name__ == "__main__":
    main()
