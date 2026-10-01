"""Exercise manual-power measurements without importing hardware drivers."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


class ManualPowerTests(unittest.TestCase):
    def test_manual_power_does_not_prompt_or_discard_the_supplied_value(self):
        for filename in ("measure_s11.py", "measure_two_port_s_paramters.py"):
            for nominal_power in (-12, -15):
                with self.subTest(filename=filename, nominal_power=nominal_power):
                    source = ROOT / filename
                    tree = ast.parse(source.read_text(), filename=str(source))
                    functions = [node for node in tree.body
                                 if isinstance(node, ast.FunctionDef)]
                    instrument = Mock()
                    responses = iter(("-3.0,-6.0\n", "0.5,0.25\n", "0.1,-0.1\n"))
                    instrument.query.side_effect = lambda command: (
                        next(responses) if command == "CALCulate:DATA:FDaTa?" else "MAN\n")
                    prompt = Mock(side_effect=EOFError("No interactive input available"))
                    namespace = {"np": np, "VNA": instrument, "input": prompt,
                                 "time": SimpleNamespace(sleep=Mock())}
                    exec(compile(ast.Module(body=functions, type_ignores=[]),
                                 str(source), "exec"), namespace)
                    with patch("builtins.print"):
                        magnitude, raw = namespace["measure_s_parameter"](
                            "S11", "TEST", 1e6, 2e9, "MAN",
                            nominal_power=nominal_power, plot=False)
                    prompt.assert_not_called()
                    commands = [call.args[0] for call in instrument.write.call_args_list]
                    self.assertIn("SOURce:POWer:ALC:MODE MAN", commands)
                    self.assertEqual([command for command in commands
                                      if command.startswith("SOURce:POWer ")],
                                     [f"SOURce:POWer {nominal_power}"])
                    np.testing.assert_allclose(magnitude, [-3.0, -6.0])
                    np.testing.assert_allclose(raw, [0.5 + 0.1j, 0.25 - 0.1j])


if __name__ == "__main__":
    unittest.main()
