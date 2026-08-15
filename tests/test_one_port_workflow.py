"""Exercise one complete S11 workflow without an instrument or dependencies."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, os.path.dirname(__file__))

import mock_instrument as mock


class FakeRawData:
    shape = (3,)


def main():
    mock.install_stubs()
    import measure_s11

    measurements = []
    initializations = []
    saved_plots = []

    def fake_measure(measurement, serial_num, start_freq, stop_freq,
                     output_power, nominal_power=-15, plot=False):
        measurements.append((measurement, serial_num, start_freq, stop_freq,
                             output_power, nominal_power, plot))
        return [0.0], FakeRawData()

    responses = iter(["y", "ANT001", "", "", "0"])
    measure_s11.input = lambda prompt="": next(responses)
    measure_s11.vna.intialize_network_analyzer = initializations.append
    measure_s11.set_freq_lims = lambda start, stop: None
    measure_s11.measure_s_parameter = fake_measure
    measure_s11.plt.savefig = saved_plots.append
    measure_s11.VISA_LIB_FILE_PATH = "C:\\Windows\\System32\\visa64.dll"
    measure_s11.TOUCHSTONE_DIR = "touchstone"
    measure_s11.SMITH_PLOT_DIR = "smith"

    measure_s11.execute_measurement(1e7, 2e9)

    expected_measurements = [
        ("S11", "ANT001_P1", 1e7, 2e9, "HIGH", -15, False),
        ("S11", "ANT001_P2", 1e7, 2e9, "HIGH", -15, False),
    ]
    assert measurements == expected_measurements
    assert initializations == ["C:\\Windows\\System32\\visa64.dll"]
    assert saved_plots == [
        os.path.join("smith", "ANT001_P1.jpg"),
        os.path.join("smith", "ANT001_P2.jpg"),
    ]
    assert ("touchstone", "ANT001_P1") in mock.TRACE
    assert ("touchstone", "ANT001_P2") in mock.TRACE

    try:
        next(responses)
    except StopIteration:
        pass
    else:
        raise AssertionError("The scripted response sequence was not consumed")

    print("One-port workflow completed once with correct P1/P2 calls and paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
