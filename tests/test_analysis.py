import unittest

from dicesim.analysis import (
    frequencies,
    summarise,
    theoretical_distribution,
    theoretical_moments,
)
from dicesim.models import DiceConfig


class AnalysisTests(unittest.TestCase):
    def test_two_d6_distribution_is_exact(self):
        dist = theoretical_distribution(DiceConfig(2, 6))
        self.assertAlmostEqual(dist[7], 6 / 36)
        self.assertAlmostEqual(dist[2], 1 / 36)
        self.assertAlmostEqual(sum(dist.values()), 1.0)
        self.assertEqual(min(dist), 2)
        self.assertEqual(max(dist), 12)

    def test_loaded_distribution_sums_to_one(self):
        dist = theoretical_distribution(DiceConfig(3, 4, (1, 2, 3, 4)))
        self.assertAlmostEqual(sum(dist.values()), 1.0)

    def test_moments_match_distribution(self):
        cfg = DiceConfig(3, 5, (1, 1, 2, 3, 5))
        dist = theoretical_distribution(cfg)
        mean = sum(k * p for k, p in dist.items())
        var = sum(p * (k - mean) ** 2 for k, p in dist.items())
        exp_mean, exp_var = theoretical_moments(cfg)
        self.assertAlmostEqual(mean, exp_mean)
        self.assertAlmostEqual(var, exp_var)

    def test_summary(self):
        s = summarise([1, 2, 2, 3, 3])
        self.assertEqual(s.modes, (2, 3))  # multimodal handled
        self.assertEqual(s.median, 2)
        self.assertAlmostEqual(s.mean, 2.2)
        self.assertEqual((s.minimum, s.maximum, s.count), (1, 3, 5))

    def test_summary_rejects_empty(self):
        with self.assertRaises(ValueError):
            summarise([])

    def test_frequencies_sorted(self):
        self.assertEqual(list(frequencies([3, 1, 3, 2])), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
