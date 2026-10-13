import random
import unittest

from dicesim.engine import simulate
from dicesim.models import DiceConfig, DiceError


class SimulateTests(unittest.TestCase):
    def test_length_and_bounds(self):
        cfg = DiceConfig(3, 6)
        out = simulate(cfg, 500, seed=1)
        self.assertEqual(len(out), 500)
        self.assertTrue(all(cfg.min_total <= x <= cfg.max_total for x in out))

    def test_seed_is_reproducible(self):
        cfg = DiceConfig(2, 6)
        self.assertEqual(simulate(cfg, 100, seed=7), simulate(cfg, 100, seed=7))
        self.assertNotEqual(simulate(cfg, 100, seed=7), simulate(cfg, 100, seed=8))

    def test_loaded_die_never_rolls_zero_weight_faces(self):
        cfg = DiceConfig(1, 4, (0, 0, 0, 1))
        self.assertEqual(set(simulate(cfg, 200, seed=3)), {4})

    def test_accepts_external_rng(self):
        out = simulate(DiceConfig(1, 6), 5, rng=random.Random(1))
        self.assertEqual(len(out), 5)

    def test_invalid_arguments(self):
        with self.assertRaises(DiceError):
            simulate(DiceConfig(), 0)
        with self.assertRaises(DiceError):
            simulate(DiceConfig(), 10, seed=1, rng=random.Random())

    def test_mean_converges_to_theory(self):
        out = simulate(DiceConfig(2, 6), 50_000, seed=42)
        self.assertAlmostEqual(sum(out) / len(out), 7.0, delta=0.05)


if __name__ == "__main__":
    unittest.main()
