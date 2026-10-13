"""Statistics: observed summary and the exact theoretical distribution."""

from __future__ import annotations

import statistics
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from .models import DiceConfig


@dataclass(frozen=True)
class Summary:
    count: int
    mean: float
    median: float
    modes: tuple[int, ...]
    variance: float
    stdev: float
    minimum: int
    maximum: int


def summarise(outcomes: Sequence[int]) -> Summary:
    """Descriptive statistics for a non-empty sequence of totals."""
    if not outcomes:
        raise ValueError("cannot summarise an empty sequence")
    return Summary(
        count=len(outcomes),
        mean=statistics.fmean(outcomes),
        median=statistics.median(outcomes),
        modes=tuple(sorted(statistics.multimode(outcomes))),
        variance=statistics.pvariance(outcomes),
        stdev=statistics.pstdev(outcomes),
        minimum=min(outcomes),
        maximum=max(outcomes),
    )


def frequencies(outcomes: Sequence[int]) -> dict[int, int]:
    """Observed counts, sorted by outcome."""
    return dict(sorted(Counter(outcomes).items()))


def theoretical_distribution(config: DiceConfig) -> dict[int, float]:
    """Exact probability of each possible total, via repeated convolution."""
    single = {face: p for face, p in enumerate(config.probabilities, start=1) if p > 0}
    dist = {0: 1.0}
    for _ in range(config.dice):
        nxt: dict[int, float] = {}
        for total, p in dist.items():
            for face, q in single.items():
                nxt[total + face] = nxt.get(total + face, 0.0) + p * q
        dist = nxt
    return dict(sorted(dist.items()))


def theoretical_moments(config: DiceConfig) -> tuple[float, float]:
    """Exact (mean, variance) of the total; dice are independent so they add."""
    probs = config.probabilities
    mean1 = sum(face * p for face, p in enumerate(probs, start=1))
    var1 = sum(p * (face - mean1) ** 2 for face, p in enumerate(probs, start=1))
    return config.dice * mean1, config.dice * var1
