# ZMP Track Record

**Zero Mass Portfolio** — Suivi de signal et historique des performances trimestrielles.

Signal BAA−AAA / GLI · Rebalancement trimestriel · Univers : IEF, TIP, GLD, FXY, FXF, LMT, CVX, SLV

---

## Signal courant

<!-- SIGNAL_START -->
| Champ | Valeur |
|---|---|
| Date | 2026-05-13 |
| Signal | **Expansion** |
| BAA−AAA spread | 0.56% |
| Seuil Protection | > 1.30% |
| GLI YoY | +13.72% |
| GLI décélération | Non |
<!-- SIGNAL_END -->

Mis à jour chaque jour ouvré à 18h00 UTC par GitHub Actions.

---

## Méthodologie

### Signal de régime

Le signal bascule en **Protection** si deux conditions sont simultanément réunies :

1. **BAA−AAA spread > 1.30 %** — écartement du crédit investment grade signalant un stress financier
2. **GLI YoY décélère** — le Global Liquidity Indicator BIS (diff. 3 trimestres sur YoY < 0)

**Hystérésis** : la sortie de Protection ne se déclenche que lorsque le spread repasse sous **1.15 %**, évitant les oscillations.

### Portefeuille

| Mode | Résistants (IEF, TIP, GLD, FXY, FXF) | Amplificateurs (LMT, CVX, SLV) |
|---|---|---|
| Expansion | 50–60% | 40–50% |
| Protection | 70–80% | 20–30% |

- **Rebalancement** : trimestriel, lookback 36 mois
- **Optimisation** : max Sharpe (SLSQP)
- **Contraintes** : 0–25% par actif, FXY/FXF réservés au mode Protection
- **Source des poids** : fichiers `quarters/YYYY-QN.json`

### Benchmarks

- **SPY** : S&P 500 ETF
- **60/40** : 60% SPY + 40% AGG (iShares Core U.S. Aggregate Bond ETF)

---

## Track Record trimestriel

> Données 2022–2025 : backtest hors échantillon (lookback 36 mois, réoptimisation trimestrielle).  
> Données 2026+ : signal et poids publiés en temps réel en début de trimestre.

| Quarter | Signal | IEF | TIP | GLD | FXY | FXF | LMT | CVX | SLV | ZMP | SPY | 60/40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022-Q1 | Expansion | 25.0% | 25.0% | 10.0% | 0.0% | 0.0% | 15.2% | 6.0% | 18.8% | +6.49% | -4.61% | -1.12% |
| 2022-Q2 | Expansion | 10.0% | 25.0% | 25.0% | 0.0% | 0.0% | 23.9% | 9.6% | 6.5% | -7.67% | -16.11% | -11.59% |
| 2022-Q3 | **Protection** | 12.5% | 24.5% | 15.5% | 12.5% | 0.0% | 7.8% | 15.7% | 11.5% | -7.36% | -4.93% | -4.76% |
| 2022-Q4 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 25.0% | 25.0% | 0.0% | +17.93% | +7.56% | +5.27% |
| 2023-Q1 | **Protection** | 12.5% | 24.5% | 15.5% | 12.5% | 0.0% | 7.1% | 15.7% | 12.2% | +0.35% | +7.46% | +5.76% |
| 2023-Q2 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 18.8% | 25.0% | 6.2% | -2.73% | +8.68% | +4.78% |
| 2023-Q3 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 12.4% | 25.0% | 12.6% | -1.17% | -3.22% | -3.20% |
| 2023-Q4 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 25.0% | 25.0% | 0.0% | +4.34% | +11.64% | +9.69% |
| 2024-Q1 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 25.0% | 25.0% | 0.0% | +3.91% | +10.39% | +5.86% |
| 2024-Q2 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 25.0% | 25.0% | 0.0% | +2.24% | +4.38% | +2.64% |
| 2024-Q3 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 25.0% | 25.0% | 0.0% | +9.24% | +5.75% | +5.57% |
| 2024-Q4 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 25.0% | 20.3% | 4.7% | -4.83% | +2.49% | +0.25% |
| 2025-Q1 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 4.0% | 25.0% | 21.0% | +9.80% | -4.27% | -1.47% |
| 2025-Q2 | Expansion | 0.0% | 25.0% | 25.0% | 0.0% | 0.0% | 25.0% | 0.0% | 25.0% | -1.61% | +10.78% | +6.95% |
| 2025-Q3 | Expansion | 7.5% | 25.0% | 25.0% | 0.0% | 0.0% | 9.9% | 7.6% | 25.0% | +12.15% | +8.12% | +5.67% |
| 2025-Q4 | Expansion | 10.0% | 25.0% | 25.0% | 0.0% | 0.0% | 7.6% | 7.4% | 25.0% | +17.21% | +3.43% | +2.43% |

### Performance cumulée 2022–2025

| Métrique | ZMP | SPY | 60/40 |
|---|---|---|---|
| CAGR (2010–2025) | +9.6% | +15.1% | — |
| Volatilité | 10.8% | 14.2% | — |
| Sharpe | 0.62 | 0.85 | — |
| Max Drawdown | -17.5% | -23.9% | — |

---

## Structure du repo

```
.github/workflows/daily_signal.yml   # Signal quotidien automatique (FRED → GitHub Actions)
compute_signal.py                     # Script de calcul du signal
signal_current.json                   # Dernier signal calculé
data/gli_current.json                 # GLI BIS (mis à jour manuellement chaque trimestre)
quarters/YYYY-QN.json                 # Poids publiés chaque début de trimestre
track_record.csv                      # Historique complet
publish_quarterly.py                  # Publie signal + poids optimisés
record_results.py                     # Enregistre la performance réalisée
```

---

## Usage

### Signal quotidien (automatique)
GitHub Actions tourne chaque jour à 18h00 UTC. Requiert le secret `FRED_API_KEY` dans les settings du repo.

### Début de trimestre
```bash
python3 publish_quarterly.py
# ou pour un trimestre spécifique :
python3 publish_quarterly.py --quarter 2026-Q2
```

### Fin de trimestre
```bash
python3 record_results.py --quarter 2026-Q1
```

### Mise à jour GLI (chaque trimestre, données BIS ~6 semaines de retard)
Éditer `data/gli_current.json` et ajouter la dernière observation trimestrielle depuis [bis.org/statistics/gli.htm](https://www.bis.org/statistics/gli.htm).

---

## Dépendances

```bash
pip install yfinance pandas scipy requests
```

---

---

© 2026 Julien Leiber. Zero Mass Portfolio methodology.  
Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).  
Commercial use requires a separate license agreement.  
Contact: contact@julienleiber.com
