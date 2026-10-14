"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import __version__
from .analysis import (
    frequencies,
    summarise,
    theoretical_distribution,
    theoretical_moments,
)
from .engine import simulate
from .models import DiceConfig, DiceError, parse_weights
from .render import frequency_table, histogram, summary_block


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dicesim",
        description="Simulate rolling (optionally loaded) dice and compare "
        "the results with the exact theoretical distribution.",
        epilog="examples:\n  dicesim 3d6 --rolls 50000 --seed 1\n"
        "  dicesim --dice 1 --faces 4 --weights 1,1,1,5 --format json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("notation", nargs="?", help="dice notation such as 2d6 "
                        "(overrides --dice/--faces)")
    parser.add_argument("--dice", type=int, default=2, help="number of dice (default: 2)")
    parser.add_argument("--faces", type=int, default=6, help="faces per die (default: 6)")
    parser.add_argument("--rolls", type=int, default=1000, help="number of rolls (default: 1000)")
    parser.add_argument("--weights",
                        help="comma-separated relative weight per face, e.g. 1,1,1,1,1,3")
    parser.add_argument("--bins", type=int, help="histogram bins (default: one per outcome)")
    parser.add_argument("--seed", type=int, help="random seed for reproducible output")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="output format (default: text)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _config_from_args(args: argparse.Namespace) -> DiceConfig:
    weights = parse_weights(args.weights) if args.weights else ()
    if args.notation:
        return DiceConfig.from_notation(args.notation, weights)
    return DiceConfig(args.dice, args.faces, weights)


def run(args: argparse.Namespace) -> str:
    config = _config_from_args(args)
    if args.bins is not None and args.bins < 1:
        raise DiceError("bins must be at least 1")
    outcomes = simulate(config, args.rolls, seed=args.seed)
    observed = frequencies(outcomes)
    expected = theoretical_distribution(config)
    summary = summarise(outcomes)
    exp_mean, exp_var = theoretical_moments(config)

    if args.format == "json":
        return json.dumps(
            {
                "config": {"dice": config.dice, "faces": config.faces,
                           "weights": list(config.weights)},
                "rolls": args.rolls,
                "seed": args.seed,
                "frequencies": observed,
                "expected_probabilities": expected,
                "summary": {
                    "mean": summary.mean, "median": summary.median,
                    "modes": list(summary.modes), "variance": summary.variance,
                    "stdev": summary.stdev, "min": summary.minimum, "max": summary.maximum,
                },
                "expected": {"mean": exp_mean, "variance": exp_var},
            },
            indent=2,
        )

    return "\n\n".join(
        [
            f"{config.dice}d{config.faces} x {args.rolls:,} rolls"
            + (f" (seed {args.seed})" if args.seed is not None else ""),
            frequency_table(observed, expected, args.rolls),
            summary_block(summary, exp_mean, exp_var),
            "Histogram\n" + histogram(outcomes, args.bins),
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args))
    except DiceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
