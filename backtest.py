"""Backtest strategies on simulated (or real, via --csv) Aviator rounds, and test for dependence."""
import argparse, csv, math, random
from strategies import ALL


def simulate(n, seed=1, edge=0.03):
    """Provably-fair style crash: P(crash >= m) = (1-edge)/m, floored at 1.00x."""
    rng = random.Random(seed)
    mults, times, t = [], [], 0.0
    for _ in range(n):
        mults.append(max(1.0, round((1 - edge) / (1 - rng.random()), 2)))
        t += rng.uniform(10, 20)          # seconds per round
        times.append(t)
    return mults, times


def load_csv(path):
    mults = [float(r[0]) for r in csv.reader(open(path)) if r]
    return mults, [i * 15.0 for i in range(len(mults))]


WINDOW = 100  # rounds of history a strategy can see (~25 min)


def run(strategy, mults, times, stake=10, hedge=False, warmup=10):
    bets = wins = 0
    profit = 0.0
    for i in range(warmup, len(mults)):
        lo = max(0, i - WINDOW)
        bet, target = strategy.decide(mults[lo:i], times[lo:i])
        if not bet:
            continue
        crash = mults[i]
        bets += 1
        wins += crash >= target
        if hedge:   # PDF 2:1 rule: big bet (2x stake) cashes at 1.5x, small bet runs to target
            profit += (stake if crash >= 1.5 else -2 * stake)
            profit += (stake * (target - 1) if crash >= target else -stake)
        else:
            profit += stake * (target - 1) if crash >= target else -stake
    return bets, wins, profit


def runs_test(mults):
    """Wald-Wolfowitz runs test on above/below 2x. |z| > 1.96 would suggest NON-randomness."""
    s = [m >= 2 for m in mults]
    n1, n2 = sum(s), len(s) - sum(s)
    runs = 1 + sum(s[i] != s[i - 1] for i in range(1, len(s)))
    mu = 2 * n1 * n2 / (n1 + n2) + 1
    var = (mu - 1) * (mu - 2) / (n1 + n2 - 1)
    return (runs - mu) / math.sqrt(var)


def conditional(mults, k=3):
    """P(next >= 2x) overall vs after k lows vs after k highs."""
    s = [m >= 2 for m in mults]
    after_low = [s[i] for i in range(k, len(s)) if not any(s[i - k:i])]
    after_high = [s[i] for i in range(k, len(s)) if all(s[i - k:i])]
    f = lambda x: sum(x) / len(x) if x else float("nan")
    return f(s), f(after_low), f(after_high), len(after_low), len(after_high)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=200_000)
    ap.add_argument("--csv", help="file with one multiplier per line (real data)")
    ap.add_argument("--hedge", action="store_true", help="use the PDF 2:1 staking rule")
    a = ap.parse_args()
    mults, times = load_csv(a.csv) if a.csv else simulate(a.rounds)

    print(f"Rounds: {len(mults):,}   hedge staking: {a.hedge}\n")
    print(f"{'Strategy':44}{'Bets':>8}{'Win%':>8}{'Profit':>12}{'ROI%':>8}")
    for s in ALL:
        b, w, p = run(s, mults, times, hedge=a.hedge)
        stake_total = b * 10 * (3 if a.hedge else 1)
        print(f"{s.name:44}{b:>8,}{(100*w/b if b else 0):>8.1f}{p:>12,.0f}{(100*p/stake_total if b else 0):>8.1f}")

    allp, lowp, highp, nl, nh = conditional(mults)
    print(f"\nRuns test z = {runs_test(mults):+.2f}   (|z|<1.96 => no evidence of a pattern)")
    print(f"P(next>=2x) overall      : {allp:.3f}")
    print(f"P(next>=2x) after 3 lows : {lowp:.3f}  (n={nl:,})")
    print(f"P(next>=2x) after 3 highs: {highp:.3f}  (n={nh:,})")
