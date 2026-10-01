"""Verify S-parameter plot units without equipment or graphical windows."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


class MagnitudeUnitTests(unittest.TestCase):
    def test_s_parameter_log_magnitude_is_labeled_db(self):
        for filename in ("scripts/vna_control.py",):
            with self.subTest(filename=filename):
                source = ROOT / filename
                tree = ast.parse(source.read_text(), filename=str(source))
                functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
                instrument = Mock()
                instrument.query.side_effect = lambda command: (
                    "0.5,0.25\n" if command == "CALCulate:DATA:FDaTa?" else "HIGH\n")
                plot = Mock()
                namespace = {"np": np, "VNA": instrument, "plt": plot,
                             "PLOT_DIR": "offline-output/",
                             "time": SimpleNamespace(sleep=Mock())}
                exec(compile(ast.Module(body=functions, type_ignores=[]),
                             str(source), "exec"), namespace)
                with patch("builtins.print"):
                    namespace["measure_s_parameter"](
                        "S11", "ANT101", 1e7, 2e9, "HIGH", plot=True)
                plot.ylabel.assert_called_once_with("dB")


if __name__ == "__main__":
    unittest.main()
