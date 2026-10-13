# dicesim



A command-line dice simulator that rolls any number of fair or **loaded** dice
and compares the results against the **exact** probability distribution, so you
can see the law of large numbers working.

> Originally a first-year coursework script (`dice_simulator.py`). Rebuilt as a
> tested, typed, installable package. See [What changed](#what-changed).

## Install

```bash
git clone https://github.com/YOUR-USERNAME/dice-game.git
cd dice-game
python -m pip install -e .
```

No third-party runtime dependencies; Python 3.9+.

## Usage

```bash
dicesim 2d6 --rolls 20000 --seed 1 --bins 4
```

```
2d6 x 20,000 rolls (seed 1)

 Total     Count   Observed   Expected
--------------------------------------
     2       575      2.88%      2.78%
     7      3324     16.62%     16.67%
   ...

            Observed  Expected
Mean           7.000     7.000
Variance       5.864     5.833

Histogram
  2-3 | ████████ 8.5%
  4-6 | ████████████████████████████████ 33.1%
  7-9 | ████████████████████████████████████████ 41.8%
10-12 | ████████████████ 16.6%
```

| Option | Meaning |
|---|---|
| `NdF` (positional) | Dice notation, e.g. `3d8`. Overrides `--dice/--faces`. |
| `--dice`, `--faces` | Number of dice and faces per die (default 2 and 6). |
| `--rolls` | Number of rolls (default 1000). |
| `--weights 1,1,1,1,1,3` | Loaded die: relative weight per face. |
| `--bins` | Histogram bins (default: one per outcome). |
| `--seed` | Reproducible results. |
| `--format json` | Machine-readable output. |

Invalid input exits with status 2 and a one-line message, never a traceback.

### As a library

```python
from dicesim import DiceConfig, simulate, summarise, theoretical_distribution

cfg = DiceConfig(dice=2, faces=6, weights=(1, 1, 1, 1, 1, 3))
totals = simulate(cfg, rolls=10_000, seed=42)
print(summarise(totals).mean)
print(theoretical_distribution(cfg)[7])
```

## Design

```
src/dicesim/
  models.py    DiceConfig: frozen, validated input; dice-notation parser
  engine.py    simulate(): seedable, batched sampling
  analysis.py  observed statistics + exact distribution (convolution)
  render.py    text table / histogram
  cli.py       argparse front end (thin; no logic of its own)
```

Simulation, statistics and presentation are separate, so each is unit-tested
alone and the CLI is a thin wrapper.

## Development

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -t . -v
ruff check . && mypy
```

## What changed

| Original | Now |
|---|---|
| One 80-line script | Layered package with a `dicesim` console command |
| Dice rolled one at a time in a Python loop | One batched, cumulative-weight draw per run |
| Global `random`, unrepeatable | Injectable RNG and `--seed` |
| Weights: ints only, errors were tracebacks or silent (negative / all-zero) | Validated floats with clear errors, exit code 2 |
| `statistics.mode` returned one value | All modes reported (`multimode`) |
| Histogram bin edges could be uneven or empty; bars scaled by a rough heuristic | Integer edges that tile the range exactly; bars scaled to the tallest bin |
| Observed results only | Observed vs. exact theoretical probabilities, mean and variance |
| No tests | 27 unit tests, CI on Python 3.9-3.13, lint and strict typing |

## License

MIT
