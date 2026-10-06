# Aviator Strategy Lab

Implements betting strategies (from a popular PDF + our own pattern ideas) as testable classes,
backtests them, and runs statistical tests for any real pattern.

    python backtest.py                 # 200k simulated rounds
    python backtest.py --hedge         # PDF 2:1 staking
    python backtest.py --csv real.csv  # your own recorded multipliers

Add a strategy: subclass `Strategy` in `strategies.py`, return `(bet, target)`, add to `ALL`.
Educational project: results show strategies do not beat the house edge. Do not gamble with real money.
