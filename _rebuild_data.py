"""Rebuild the archive's text layer from the PDFs + the hand-checked fix
files, in the one order that works (verified 2026-10-11: the result equals
the committed kengura-archive.json). Run with plain `python` (PyMuPDF).

  1 _reextract_solutions.py   official solutions from the booklets
  2 _fix_keys_audit.py        audited keys + patched official texts
  3 _apply_clean_solutions.py cleaned official texts + booklet typos
  4 _apply_audit_text.py      prompts / options transcribed from figures
  5 _apply_kid_solutions.py   kid solutions + misconceptions
  6 _mechanic_review.py       trick-tag corrections
  7 _fix_typos_2026.py        spelling slips
Then `node _smoke_test.cjs`. Figures are separate: _recrop.py, then
_trim_figures.py, then bump FIGS in sw.js.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for step in ['_reextract_solutions.py', '_fix_keys_audit.py', '_apply_clean_solutions.py',
             '_apply_audit_text.py', '_apply_kid_solutions.py', '_mechanic_review.py', '_fix_typos_2026.py']:
    print('==', step, flush=True)
    subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, step)], cwd=HERE, check=True)
subprocess.run(['node', os.path.join(HERE, '_smoke_test.cjs')], cwd=HERE, check=True)
