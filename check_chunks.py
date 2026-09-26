"""Criterion 4: every chunk is 200-700 characters and ends on a complete sentence."""
import json
import sys

import config
from chunker import split_documents
from ingest import load_documents

chunks = split_documents(load_documents())
bad = []
for c in chunks:
    text = c.text.strip()
    reasons = []
    if len(text) < 200:
        reasons.append(f"too short ({len(text)})")
    if len(text) > 700:
        reasons.append(f"too long ({len(text)})")
    if text[-1] not in ".!?\"'”)*":
        reasons.append(f"ends mid-sentence: ...{text[-40:]!r}")
    if reasons:
        bad.append({"chunk": f"{c.source}#{c.index}", "reasons": reasons})

lengths = [len(c.text.strip()) for c in chunks]
print(f"{len(chunks)} chunks, min {min(lengths)}, max {max(lengths)}, "
      f"{len(bad)} violating")
for b in bad:
    print(" ", b["chunk"], "; ".join(b["reasons"]))
label = sys.argv[1] if len(sys.argv) > 1 else "run"
config.RESULTS_DIR.mkdir(exist_ok=True)
(config.RESULTS_DIR / f"chunks_{label}.json").write_text(
    json.dumps({"n": len(chunks), "min": min(lengths), "max": max(lengths),
                "violations": bad}, indent=2))
