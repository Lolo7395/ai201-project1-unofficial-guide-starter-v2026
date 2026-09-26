"""
Scorer for run_eval.py. Judges each run against criteria 1, 2 and 5 from
criteria.md, using each question's `expects` phrase from questions.py.

  1. Some retrieved chunk contains `expects`.
  2. The answer names at least one source file (guide_*.md).
  5. At least one cited file actually contains `expects`.

`judge` returns True only when the run passes all three. Every call is also
recorded per criterion, and written to results/criteria_<label>.json on exit so
the README table can be built from real numbers. Criterion 3 comes from
run_eval.py's gate check; criterion 4 from check_chunks.py.
"""

import atexit
import json
import re
import sys
from pathlib import Path

import config

_records: list[dict] = []
SOURCE_RE = re.compile(r"guide_[a-z_]+\.md")


def _norm(text: str) -> str:
    """Lowercase and collapse whitespace so line wrapping can't hide a match."""
    return re.sub(r"\s+", " ", text).lower()


def _file_text(name: str) -> str:
    path = config.corpus_path() / name
    return _norm(path.read_text(encoding="utf-8")) if path.exists() else ""


def judge(question: str, expects: str, answer: str, results) -> bool:
    want = _norm(expects)
    c1 = any(want in _norm(r.text) for r in results)
    cited = sorted(set(SOURCE_RE.findall(answer)))
    c2 = bool(cited)
    c5 = any(want in _file_text(f) for f in cited)
    _records.append(
        {"question": question, "expects": expects, "c1": c1, "c2": c2,
         "c5": c5, "cited": cited,
         "retrieved": [r.label for r in results]}
    )
    return c1 and c2 and c5


def _dump():
    if not _records:
        return
    label = ""
    if "--label" in sys.argv:
        label = sys.argv[sys.argv.index("--label") + 1]
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"criteria_{label or 'run'}.json"
    path.write_text(json.dumps(_records, indent=2), encoding="utf-8")


atexit.register(_dump)
