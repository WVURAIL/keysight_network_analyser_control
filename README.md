# keysight_network_analyser_control

> Archived 20 August 2026. This is a read-only historical snapshot; no hardware
> support or ongoing maintenance is provided.

Python scripts for collecting one-port and two-port S-parameters from a
Keysight FieldFox network analyser. This is the canonical archive for the
scripts; a frozen 2021 copy also remains in
[`WVURAIL/rflab_test`](https://github.com/WVURAIL/rflab_test/tree/master/keysight_na)
to preserve that repository's old paths.

## Layout

```text
scripts/
  vna_control.py                    Shared instrument and SCPI helpers
  measure_s11.py                    One-port S11 workflow
  measure_two_port_s_paramters.py   Two-port workflow
legacy/
  measure_s11_original.py           Exact pre-refactor source
  measure_two_port_s_paramters_original.py
tests/
  test_scpi_unchanged.py            Mock check of the historical SCPI sequence
  test_one_port_workflow.py         Mock check of the complete S11 workflow
```

The misspelling `paramters` is retained because it is part of the historical
filename and may appear in links. Root-level files with the same names are
relocation notices for old branch-based URLs.

## Validation without hardware

The tests use standard-library stubs, so they do not require an analyser, VISA
runtime, or the packages in `requirements.txt`:

```console
python3 -S tests/test_scpi_unchanged.py
python3 -S tests/test_one_port_workflow.py
```

They verify that the shared helpers preserve the original SCPI sequence and
that one complete S11 iteration uses the correct P1/P2 arguments, output names,
and exit path. They do not establish compatibility with a physical instrument.

## Historical environment

`requirements.txt` records the package versions documented in 2021:

```text
matplotlib==3.3.4
numpy==1.19.2
PyVISA==1.11.3
scikit_rf==0.18.1
```

Treat these pins as provenance, not as a promise that they install on a current
Python release. The scripts were developed for Windows and require either the
[Keysight IO Libraries Suite](https://www.keysight.com/find/iosuite)
or another PyVISA-compatible VISA implementation.

## Running the historical workflows

Review the scripts before connecting hardware. Set `PARENT_DIR` in the selected
script. The one-port script also passes its `VISA_LIB_FILE_PATH` explicitly;
the two-port script lets PyVISA discover a VISA library.

```console
python scripts/measure_s11.py
python scripts/measure_two_port_s_paramters.py
```

Both workflows select the first VISA resource returned by the local runtime.
Confirm that it is the intended analyser before use. Linux operation was never
completed, and no instrument was available for the 2026 archive review. The
response parser and command set remain specific to the original FieldFox
workflow.

The archive review corrected five deterministic defects: a missing `os` import,
the one-port P2 function arguments, the P2 Smith-chart filename, the loop exit
comparison, and a manual-power prompt whose response was discarded.
Hardware-sensitive behavior was otherwise left unchanged.

## History, contributors, and licence

All original commits through
[`72df04d`](https://github.com/WVURAIL/keysight_network_analyser_control/commit/72df04d44f07f7882b8d71fbe554d28221c74b57)
remain unchanged and reachable. The archive commit keeps exact pre-refactor
scripts in `legacy/`, extracts their duplicate control functions into
`scripts/vna_control.py`, and adds mock validation.

The copy in `rflab_test` first matched this repository at
[`406cdfc`](https://github.com/WVURAIL/keysight_network_analyser_control/commit/406cdfc78b786a7f1275d0f43ea1f88a54fc0cbc).
Its later two-port adjustment was already present here, so no unique controller
functionality needed to be merged from the copy.

Git history records work by Pranav Sanghavi and Joseph Shepard. The repository
is distributed under the MIT License; see [`LICENSE`](LICENSE).
