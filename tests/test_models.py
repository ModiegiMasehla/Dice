import unittest

from dicesim.models import DiceConfig, DiceError, parse_weights


class DiceConfigTests(unittest.TestCase):
    def test_defaults_to_fair_dice(self):
        cfg = DiceConfig(2, 6)
        self.assertEqual(cfg.weights, (1.0,) * 6)
        self.assertAlmostEqual(sum(cfg.probabilities), 1.0)

    def test_totals_range(self):
        cfg = DiceConfig(3, 8)
        self.assertEqual((cfg.min_total, cfg.max_total), (3, 24))

    def test_rejects_bad_values(self):
        bad = [
            dict(dice=0), dict(dice=-1), dict(faces=1),
            dict(faces=3, weights=(1, 2)),         # wrong length
            dict(faces=2, weights=(-1, 2)),        # negative
            dict(faces=2, weights=(0, 0)),         # all zero
            dict(faces=2, weights=(float("nan"), 1)),
            dict(faces=2, weights=(float("inf"), 1)),
        ]
        for kwargs in bad:
            with self.subTest(kwargs=kwargs), self.assertRaises(DiceError):
                DiceConfig(**kwargs)

    def test_notation(self):
        self.assertEqual(DiceConfig.from_notation("3d8"), DiceConfig(3, 8))
        self.assertEqual(DiceConfig.from_notation(" 2D6 "), DiceConfig(2, 6))
        for text in ("d6", "2x6", "2d", "", "2d6d"):
            with self.subTest(text=text), self.assertRaises(DiceError):
                DiceConfig.from_notation(text)

    def test_parse_weights(self):
        self.assertEqual(parse_weights("1, 2,3.5"), (1.0, 2.0, 3.5))
        with self.assertRaises(DiceError):
            parse_weights("1,a")


if __name__ == "__main__":
    unittest.main()
