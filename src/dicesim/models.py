"""Domain model: a validated description of the dice being rolled."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

MAX_DICE = 1_000
MAX_FACES = 10_000
_NOTATION = re.compile(r"^\s*(\d+)\s*[dD]\s*(\d+)\s*$")


class DiceError(ValueError):
    """Raised when dice parameters are invalid."""


@dataclass(frozen=True)
class DiceConfig:
    """A set of identical dice, optionally loaded (weighted).

    Faces are numbered ``1..faces``. ``weights[i]`` is the relative
    likelihood of face ``i + 1``; weights need not sum to 1.
    """

    dice: int = 2
    faces: int = 6
    weights: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if not 1 <= self.dice <= MAX_DICE:
            raise DiceError(f"dice must be between 1 and {MAX_DICE}, got {self.dice}")
        if not 2 <= self.faces <= MAX_FACES:
            raise DiceError(f"faces must be between 2 and {MAX_FACES}, got {self.faces}")
        weights = tuple(float(w) for w in self.weights) or (1.0,) * self.faces
        if len(weights) != self.faces:
            raise DiceError(
                f"expected {self.faces} weights (one per face), got {len(weights)}"
            )
        if any(w < 0 or w != w or w == float("inf") for w in weights):
            raise DiceError("weights must be finite and non-negative")
        if sum(weights) <= 0:
            raise DiceError("at least one weight must be greater than zero")
        object.__setattr__(self, "weights", weights)

    @property
    def probabilities(self) -> tuple[float, ...]:
        """Per-face probabilities (weights normalised to sum to 1)."""
        total = sum(self.weights)
        return tuple(w / total for w in self.weights)

    @property
    def min_total(self) -> int:
        return self.dice

    @property
    def max_total(self) -> int:
        return self.dice * self.faces

    @classmethod
    def from_notation(
        cls, notation: str, weights: Sequence[float] = ()
    ) -> "DiceConfig":
        """Build a config from standard dice notation, e.g. ``"3d8"``."""
        match = _NOTATION.match(notation)
        if not match:
            raise DiceError(f"invalid dice notation {notation!r}; expected e.g. '2d6'")
        return cls(int(match[1]), int(match[2]), tuple(weights))


def parse_weights(text: str) -> tuple[float, ...]:
    """Parse ``"1,1,2,4"`` into a tuple of floats."""
    try:
        return tuple(float(part) for part in text.split(","))
    except ValueError as exc:
        raise DiceError(f"weights must be comma-separated numbers, got {text!r}") from exc
