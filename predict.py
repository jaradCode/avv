"""Type in recent multipliers -> every strategy votes BET / DO NOT BET for the next rounds.

    python predict.py 1.2 3.4 1.1 2.5 1.8
    python predict.py                      (it will ask you to type them)
    python predict.py 1.2 3.4 1.1 --pink-ago 4.5   (last 10x+ was 4.5 minutes ago)
"""
import argparse
from strategies import LowStreak, Alternating, PinkTimer, OnesSeed

STRATS = [LowStreak(), Alternating(), PinkTimer(), OnesSeed()]
ROUND_SECONDS = 15


def vote(mults, times):
    fired = []
    for s in STRATS:
        bet, target = s.decide(mults, times)
        if bet:
            fired.append((s.name, target))
    return fired


def history(mults, pink_ago):
    times = [i * ROUND_SECONDS for i in range(len(mults))]
    if pink_ago is not None:           # fake a pink so the time strategy can see it
        mults = [10.0] + mults
        end = times[-1] if times else 0
        times = [end - pink_ago * 60] + times
    return mults, times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rounds", nargs="*", type=float)
    ap.add_argument("--pink-ago", type=float, help="minutes since the last 10x+ round")
    a = ap.parse_args()
    rounds = a.rounds or [float(x) for x in input("Enter last rounds (e.g. 1.2 3.4 1.1 2.5 1.8): ").replace(",", " ").split()]

    mults, times = history(rounds, a.pink_ago)
    print(f"\nInput: {rounds}\n")
    for i in range(1, 6):
        fired = vote(mults, times)
        if fired:
            target = max(t for _, t in fired)
            print(f"Round +{i}:  BET  (cash out around {target:g}x)   <- {len(fired)} strategy signal(s)")
            for name, t in fired:
                print(f"            - {name}")
            guess = target
        else:
            print(f"Round +{i}:  DO NOT BET")
            guess = 1.5
        mults, times = mults + [guess], times + [times[-1] + ROUND_SECONDS]  # projection: feed the guess back in
    print("\nNote: rounds +2..+5 are projections built on the earlier guesses, not real data.")
    print("Backtests show these signals hit ~48% (a coin flip) and lose to the house edge over time.")


if __name__ == "__main__":
    main()
