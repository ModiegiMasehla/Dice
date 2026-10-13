import unittest

from dicesim.render import bin_edges, histogram


class BinEdgesTests(unittest.TestCase):
    def test_covers_range_without_gaps_or_overlap(self):
        for low, high, bins in [(2, 12, 3), (2, 12, 11), (1, 100, 7), (5, 5, 4)]:
            with self.subTest(low=low, high=high, bins=bins):
                edges = bin_edges(low, high, bins)
                self.assertEqual(edges[0], low)
                self.assertEqual(edges[-1], high + 1)
                self.assertEqual(edges, sorted(set(edges)))

    def test_bins_capped_to_span(self):
        self.assertEqual(len(bin_edges(1, 3, 50)) - 1, 3)


class HistogramTests(unittest.TestCase):
    def test_percentages_sum_to_100(self):
        out = histogram([1, 1, 2, 3, 3, 3, 4, 4], bins=2)
        pcts = [float(line.rsplit(" ", 1)[1].rstrip("%")) for line in out.splitlines()]
        self.assertAlmostEqual(sum(pcts), 100.0, delta=0.2)

    def test_tallest_bar_fills_width(self):
        out = histogram([1, 2, 2, 2], width=10)
        self.assertEqual(max(line.count("█") for line in out.splitlines()), 10)

    def test_single_value(self):
        self.assertIn("100.0%", histogram([4, 4, 4]))


if __name__ == "__main__":
    unittest.main()
