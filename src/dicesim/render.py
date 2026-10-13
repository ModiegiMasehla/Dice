"""Plain-text rendering of results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .analysis import Summary


def bin_edges(low: int, high: int, bins: int) -> list[int]:
    """Integer bin boundaries covering ``low..high`` inclusive.

    Returns ``bins + 1`` edges; bin ``i`` holds ``edges[i] <= x < edges[i+1]``.
    ``bins`` is capped at the number of distinct values so no bin is empty
    by construction.
    """
    span = high - low + 1
    bins = max(1, min(bins, span))
    return [low + (i * span) // bins for i in range(bins)] + [high + 1]


def histogram(outcomes: Sequence[int], bins: int | None = None, width: int = 40) -> str:
    """Horizontal bar chart; bars are scaled so the tallest fills ``width``."""
    low, high = min(outcomes), max(outcomes)
    edges = bin_edges(low, high, bins or (high - low + 1))
    counts = [0] * (len(edges) - 1)
    for value in outcomes:
        # Walk edges from the right; bin counts are small so this is cheap.
        for i in range(len(counts) - 1, -1, -1):
            if value >= edges[i]:
                counts[i] += 1
                break
    peak = max(counts)
    labels = [
        f"{edges[i]}" if edges[i + 1] - edges[i] == 1 else f"{edges[i]}-{edges[i + 1] - 1}"
        for i in range(len(counts))
    ]
    pad = max(len(label) for label in labels)
    total = len(outcomes)
    lines = []
    for label, count in zip(labels, counts):
        bar = "█" * round(count / peak * width) if peak else ""
        lines.append(f"{label:>{pad}} | {bar} {count / total:.1%}")
    return "\n".join(lines)


def frequency_table(
    observed: Mapping[int, int], expected: Mapping[int, float], total: int
) -> str:
    """Observed vs. theoretical frequency for every possible total."""
    header = f"{'Total':>6}  {'Count':>8}  {'Observed':>9}  {'Expected':>9}"
    rows = [header, "-" * len(header)]
    for outcome in sorted(set(observed) | set(expected)):
        count = observed.get(outcome, 0)
        rows.append(
            f"{outcome:>6}  {count:>8}  {count / total:>9.2%}  {expected.get(outcome, 0):>9.2%}"
        )
    return "\n".join(rows)


def summary_block(summary: Summary, expected_mean: float, expected_var: float) -> str:
    modes = ", ".join(map(str, summary.modes))
    return "\n".join(
        [
            f"{'':<10}{'Observed':>10}{'Expected':>10}",
            f"{'Mean':<10}{summary.mean:>10.3f}{expected_mean:>10.3f}",
            f"{'Variance':<10}{summary.variance:>10.3f}{expected_var:>10.3f}",
            f"{'Std dev':<10}{summary.stdev:>10.3f}{expected_var ** 0.5:>10.3f}",
            f"{'Median':<10}{summary.median:>10}",
            f"{'Mode':<10}{modes:>10}",
            f"{'Range':<10}{f'{summary.minimum}-{summary.maximum}':>10}",
        ]
    )
