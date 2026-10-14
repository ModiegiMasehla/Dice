"""dicesim: a small, tested dice-roll simulator."""

from .analysis import Summary, summarise, theoretical_distribution
from .engine import simulate
from .models import DiceConfig, DiceError

__version__ = "1.0.0"
__all__ = [
    "DiceConfig",
    "DiceError",
    "Summary",
    "simulate",
    "summarise",
    "theoretical_distribution",
    "__version__",
]
