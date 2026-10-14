"""Simulation engine: rolls dice using an injectable random generator."""

from __future__ import annotations

import random
from itertools import accumulate

from .models import DiceConfig, DiceError


def simulate(
    config: DiceConfig,
    rolls: int,
    *,
    seed: int | None = None,
    rng: random.Random | None = None,
) -> list[int]:
    """Roll ``config.dice`` dice ``rolls`` times and return each total.

    Pass ``seed`` for reproducible runs, or an existing ``rng`` to share
    state with other code. All dice are drawn in one batched call, which is
    far faster than sampling one die at a time.
    """
    if rolls < 1:
        raise DiceError(f"rolls must be at least 1, got {rolls}")
    if rng is not None and seed is not None:
        raise DiceError("pass either seed or rng, not both")
    rng = rng or random.Random(seed)

    cum_weights = list(accumulate(config.weights))
    faces = range(1, config.faces + 1)
    draws = rng.choices(faces, cum_weights=cum_weights, k=rolls * config.dice)
    n = config.dice
    return [sum(draws[i : i + n]) for i in range(0, len(draws), n)]
