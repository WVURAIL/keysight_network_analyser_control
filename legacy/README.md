# Pre-refactor originals

These are the two root-level scripts exactly as they appeared at the original
repository tip, `72df04d`. They are retained as working-tree files so a future
reader can compare the archive-reviewed layout without reconstructing an older
commit.

Do not run these versions. The original `measure_s11.py` uses `os.path` without
importing `os` and contains the workflow defects documented in the root README.
The archive-reviewed scripts live in `scripts/`.
