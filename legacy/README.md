# Pre-refactor originals

The two scripts exactly as they were before the shared `vna_control.py`
module was extracted, kept as working-tree files so that comparing against
the originals never requires archaeology in git history.

The refactor commit's message said these were preserved here; they were not —
that commit put them only in history. This directory makes the claim true.

Do not run these: `measure_s11.py` in this original form crashes with a
`NameError` (it used `os.path` without importing `os`). The maintained
scripts live in `scripts/`.
