"""Each strategy looks at past rounds and returns (bet, target_multiplier) for the NEXT round."""
from dataclasses import dataclass

SKIP = (False, 0.0)


class Strategy:
    name = "base"
    def decide(self, mults, times):
        raise NotImplementedError


class AlwaysBet(Strategy):
    """Baseline: bet every round. Any real strategy must beat this."""
    name = "Baseline: always bet @2x"
    def decide(self, mults, times):
        return True, 2.0


@dataclass
class LowStreak(Strategy):
    """User pattern: after N rounds below 2x, expect one above 2x -> bet. After N highs, skip."""
    n: int = 3
    name = "Low-streak rebound (3 below 2x -> bet)"
    def decide(self, mults, times):
        last = mults[-self.n:]
        if len(last) == self.n and all(m < 2 for m in last):
            return True, 2.0
        return SKIP


@dataclass
class Alternating(Strategy):
    """User pattern: H,L,H,L... keeps alternating. Predict the next flip, bet if next is H."""
    name = "Alternating pattern (H/L flip)"
    def decide(self, mults, times):
        if len(mults) < 4:
            return SKIP
        h = [m >= 2 for m in mults[-4:]]
        if all(h[i] != h[i + 1] for i in range(3)):   # strict alternation
            return (True, 2.0) if not h[-1] else SKIP  # last was L -> predict H
        return SKIP


@dataclass
class PinkTimer(Strategy):
    """PDF 'time strategy': after a 10x+ ('pink'), bet 4-6 min later, give up after the window."""
    lo: float = 240
    hi: float = 360
    name = "PDF time strategy (pink + 4-6 min)"
    def decide(self, mults, times):
        for m, t in zip(reversed(mults), reversed(times)):
            if m >= 10:
                return (True, 10.0) if self.lo <= times[-1] - t <= self.hi else SKIP
        return SKIP


@dataclass
class OnesSeed(Strategy):
    """PDF: a run of ~1x rounds is 'a sign a big multiplier is coming'."""
    k: int = 3
    name = "PDF 1x-seed (3 near-1x -> bet 5x)"
    def decide(self, mults, times):
        last = mults[-self.k:]
        if len(last) == self.k and all(m < 1.2 for m in last):
            return True, 5.0
        return SKIP


ALL = [AlwaysBet(), LowStreak(), Alternating(), PinkTimer(), OnesSeed()]
