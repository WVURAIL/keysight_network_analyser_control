"""Offline regression checks; no VISA modules or equipment are accessed."""

import ast
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call, create_autospec, patch

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]


class OnePortWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.source = REPO_ROOT / "scripts" / "measure_s11.py"
        self.tree = ast.parse(self.source.read_text(), filename=str(self.source))

    def run_fragment(self, nodes, namespace):
        fragment = ast.Module(body=nodes, type_ignores=[])
        exec(compile(fragment, str(self.source), "exec"), namespace)

    def workflow_namespace(self, responses):
        networks = [Mock(), Mock()]
        namespace = {
            "np": np,
            "vna": SimpleNamespace(intialize_network_analyzer=Mock()),
            "VISA_LIB_FILE_PATH": "offline-library",
            "rf": SimpleNamespace(Network=Mock(side_effect=networks)),
            "plt": Mock(),
            "input": Mock(side_effect=responses),
            "TOUCHSTONE_DIR": "/measurements/touchstone",
            "SMITH_PLOT_DIR": "/measurements/smith/",
        }
        # Defining functions does not run their bodies or import VISA.
        functions = [node for node in self.tree.body
                     if isinstance(node, ast.FunctionDef)]
        os_imports = [node for node in self.tree.body
                      if isinstance(node, ast.Import)
                      and any(alias.name == "os" for alias in node.names)]
        control_source = REPO_ROOT / "scripts" / "vna_control.py"
        control_tree = ast.parse(control_source.read_text(), filename=str(control_source))
        measurement_helper = next(node for node in control_tree.body
                                  if isinstance(node, ast.FunctionDef)
                                  and node.name == "measure_s_parameter")
        self.run_fragment(os_imports + functions + [measurement_helper], namespace)
        namespace["set_freq_lims"] = Mock()
        namespace["measure_s_parameter"] = create_autospec(
            namespace["measure_s_parameter"],
            return_value=(np.array([0.0, 0.0]), np.array([0.6 + 0.8j, 0.2j])),
        )
        return namespace, networks

    def test_output_directories_initialize_from_source_imports(self):
        imports = [node for node in self.tree.body
                   if isinstance(node, ast.Import)
                   and any(alias.name == "os" for alias in node.names)]
        main = next(node for node in self.tree.body
                    if isinstance(node, ast.If)
                    and "__name__" in ast.unparse(node.test))
        directory_checks = [node for node in main.body
                            if isinstance(node, ast.If)
                            and "os.path.exists" in ast.unparse(node.test)]
        self.assertEqual(len(directory_checks), 3)
        with tempfile.TemporaryDirectory() as folder:
            paths = {
                "PLOT_DIR": str(Path(folder) / "plots"),
                "TOUCHSTONE_DIR": str(Path(folder) / "touchstone"),
                "SMITH_PLOT_DIR": str(Path(folder) / "smith"),
            }
            namespace = dict(paths)
            self.run_fragment(imports + directory_checks, namespace)
            for value in paths.values():
                self.assertTrue(Path(value).is_dir())

    def test_both_ports_are_saved_under_distinct_serial_names(self):
        namespace, networks = self.workflow_namespace(["y", "ANT42", "", "", "0"])
        with patch("builtins.print"):
            namespace["execute_measurement"](1e7, 2e9)
        namespace["measure_s_parameter"].assert_has_calls([
            call("S11", "ANT42_P1", 1e7, 2e9, "HIGH", nominal_power=-15, plot=False),
            call("S11", "ANT42_P2", 1e7, 2e9, "HIGH", nominal_power=-15, plot=False),
        ])
        self.assertEqual(namespace["measure_s_parameter"].call_count, 2)
        for network, serial in zip(networks, ["ANT42_P1", "ANT42_P2"]):
            network.write_touchstone.assert_called_once_with(
                filename=serial, dir="/measurements/touchstone")
        self.assertEqual(namespace["plt"].savefig.call_args_list, [
            call("/measurements/smith/ANT42_P1.jpg"),
            call("/measurements/smith/ANT42_P2.jpg"),
        ])
        self.assertEqual(namespace["input"].call_count, 5)

    def test_zero_exits_and_one_repeats_without_connecting(self):
        for responses in (["n", "0"], ["n", "1", "n", "0"]):
            with self.subTest(responses=responses):
                namespace, _ = self.workflow_namespace(responses)
                with patch("builtins.print"):
                    namespace["execute_measurement"](1e7, 2e9)
                self.assertEqual(namespace["input"].call_count, len(responses))
                namespace["vna"].intialize_network_analyzer.assert_not_called()
                namespace["measure_s_parameter"].assert_not_called()


if __name__ == "__main__":
    unittest.main()
