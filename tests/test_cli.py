import contextlib
import io
import json
import unittest

from dicesim.cli import main


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exc:  # argparse exits on --help / bad flags
            code = exc.code
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def test_default_run(self):
        code, out, _ = run_cli("--seed", "1")
        self.assertEqual(code, 0)
        for section in ("Total", "Observed", "Histogram"):
            self.assertIn(section, out)

    def test_notation_and_seed_are_deterministic(self):
        a = run_cli("3d6", "--rolls", "200", "--seed", "5")
        b = run_cli("3d6", "--rolls", "200", "--seed", "5")
        self.assertEqual(a, b)
        self.assertIn("3d6 x 200 rolls", a[1])

    def test_json_output_is_valid(self):
        code, out, _ = run_cli("1d4", "--weights", "1,1,1,5", "--format", "json",
                               "--rolls", "300", "--seed", "2")
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(sum(data["frequencies"].values()), 300)
        self.assertAlmostEqual(sum(data["expected_probabilities"].values()), 1.0)

    def test_user_errors_exit_2_without_traceback(self):
        cases = [
            ("--weights", "1,2"),
            ("--weights", "a,b,c,d,e,f"),
            ("--dice", "0"),
            ("--rolls", "0"),
            ("--bins", "0"),
            ("7x7",),
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                code, _, err = run_cli(*argv)
                self.assertEqual(code, 2)
                self.assertTrue(err.startswith("error:"))
                self.assertNotIn("Traceback", err)

    def test_version(self):
        code, out, _ = run_cli("--version")
        self.assertEqual(code, 0)
        self.assertIn("dicesim", out)


if __name__ == "__main__":
    unittest.main()
