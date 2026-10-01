"""
Checks that the shared helpers emit the SCPI sequence they always did.

There is no network analyser in CI, so this stands in a fake instrument that
records every write and query, drives the helpers with fixed inputs, and
compares the result against the sequence recorded here from the pre-refactor
scripts. If a change alters what goes out on the wire, this fails.

    python3 tests/test_scpi_unchanged.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, os.path.dirname(__file__))

import mock_instrument as mock

EXPECTED = [
    ("write", "SENSe:FREQuency:STARt 1000000.0"),
    ("write", "SENSe:FREQuency:STOp 2000000000.0"),
    ("query", "SOURce:POWer:ALC:MODE?"),
    ("write", "SOURce:POWer:ALC:MODE MAN"),
    ("query", "SOURce:POWer:ALC:MODE?"),
    ("write", "SOURce:POWer -12"),
    ("write", "SOURce:POWer:ALC:MODE HIGH"),
    ("query", "SOURce:POWer:ALC:MODE?"),
]


def main():
    mock.install_stubs()
    import vna_control

    mock.TRACE.clear()
    vna_control.VNA = mock.MockVNA()
    vna_control.set_freq_lims(1e6, 2e9)
    vna_control.check_power_mode()
    vna_control.set_power_mode("MAN", -12)
    vna_control.set_power_mode("HIGH")
    got = list(mock.TRACE)

    if got != EXPECTED:
        print("SCPI sequence changed.")
        for want, have in zip(EXPECTED, got):
            print(f"  {'ok ' if want == have else 'DIFF'}  expected {want}  got {have}")
        return 1

    # the VISA library argument must still reach ResourceManager unchanged
    mock.TRACE.clear()
    vna_control.intialize_network_analyzer("C:\\Windows\\System32\\visa64.dll")
    assert ("ResourceManager", "C:\\Windows\\System32\\visa64.dll") in mock.TRACE
    mock.TRACE.clear()
    vna_control.intialize_network_analyzer()
    assert ("ResourceManager", None) in mock.TRACE

    # MAN mode must honor nominal_power without stopping for discarded input.
    mock.TRACE.clear()
    vna_control.VNA = mock.MockVNA()
    vna_control.time.sleep = lambda seconds: None
    vna_control.input = lambda prompt="": (_ for _ in ()).throw(
        AssertionError("measure_s_parameter unexpectedly prompted for input"))
    vna_control.measure_s_parameter(
        "S11", "TEST", 1e6, 2e9, "MAN", nominal_power=-12, plot=False)
    assert ("write", "SOURce:POWer -12") in mock.TRACE

    print(f"SCPI sequence unchanged ({len(got)} commands), VISA selection and manual power preserved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
