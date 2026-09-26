# The Unofficial Guide

Lorraine Mureya — corpus: `city_guides`.

---

# Unit 1

## What This Does

The Unofficial Guide is a question-answering tool built from 14 short travel guides to a fictional region. The guides cover places like Brightwater, Kestrelford, Corry Vale, Halden Bay, and Marchwood, as well as topics like transport, food, accessibility, walking, and seasons.

You can ask a practical question, such as “Does a bus run to Kestrelford on Sundays?” The tool searches the guides for relevant sections and uses them to answer, naming the guide it used. If the guides don’t contain a relevant answer, it says so instead of guessing.
To use it, run `python app.py index` first, then `python app.py ask "your question"`.
.

## Chunking Strategy
**Chunk size:** Each chunk usually contains one `##` section. Sections shorter than 180 characters are merged with the next section. The resulting index has 91 chunks, ranging from 201 to 678 characters, with an average of 327.

**Overlap:** I use 90 characters of overlap only when a paragraph is too long and must be split at a sentence ending. Splits between whole paragraphs have no overlap.

In Milestone 1, I found that the guides are organized into short sections such as “Getting there,” “Where to stay,” and “When to go.” Each section usually covers one topic, and an answer like the cost of climbing a tower fits within one section. Splitting at a fixed character count could cut an answer away from its context or combine unrelated topics. Keeping sections together works better for these guides.

I also add the guide title and section heading to each chunk. That way, a sentence like “There is no local bus service” clearly belongs to a particular town, and the town name is included when the chunk is indexed.

I made one change after testing my first version. I initially split long sections by sentence, but this caused some accessibility guide chunks to begin in the middle of a thought and lose their paragraph breaks. Since each paragraph in that guide covers one town, I now keep paragraphs together whenever possible. I split by sentence only when a single paragraph is too long.


## Sample Chunks

All five printed from the built index; each was produced by
`chunker.py::split_documents`.

**Chunk 1** — source: `guide_kestrelford.md` — produced by: `chunker.py::split_documents`

```
Kestrelford — Getting there
No railway station; the line was closed in 1963 and the trackbed is now a walking route. Buses run from Brightwater roughly hourly on weekdays, every two hours on Saturdays, and not at all on Sundays. Driving takes 55 minutes and the last eight are on a single-track road with passing places.
```

**Chunk 2** — source: `guide_corry_vale.md` — produced by: `chunker.py::split_documents`

```
Corry Vale — Eat and drink
One pub in the largest village serves food seven days a week. A second, in the third village, opens Thursday to Sunday. There is a farm shop at the valley mouth that sells bread, cheese and little else, and it closes at 4pm. Bring supplies; this is not a place with options.
```

**Chunk 3** — source: `guide_regional_transport.md` — produced by: `chunker.py::split_documents`

```
Getting around the region — Buses
Three operators run in the region and they do not accept each other's tickets,
which is the single most common source of confusion for visitors. Services
concentrate on weekday daytimes. Sunday service is minimal to non-existent
outside the Brightwater town routes.

The Kestrelford service is hourly on weekdays, two-hourly on Saturdays, and
does not run on Sundays. The Halden Bay coast service runs four times daily
year-round.
```

**Chunk 4** — source: `guide_accessibility.md` — produced by: `chunker.py::split_documents`

```
Getting around the region with limited mobility — Difficult
**Kestrelford** is built on a slope and the walk up from the lower car park is
steeper than it looks on a map. There is no transport within the town.

**Halden Bay** is built on three levels connected by stepped lanes. The harbour
front is level; everything above it is not. This is hard going with luggage or a
pushchair, let alone a wheelchair.

**Corry Vale** has no public transport, villages two to four miles apart, and
footpaths rather than pavements. **Elder Ness** is shingle and a single street.
```

**Chunk 5** — source: `guide_eating.md` — produced by: `chunker.py::split_documents`

```
Eating across the region — Opening hours
This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

## Sample Answer

**Question:** Can I get a taxi in Corry Vale without booking ahead?

**Answer:**

```
No, you cannot. There is only one taxi in the valley, and it must be booked a day ahead (guide_corry_vale.md).

Sources retrieved: guide_corry_vale.md
```

**My relevance cutoff is `THRESHOLD = 0.6` in `config.py`.** A lower distance means a closer match. For my five questions answered by the guides, the closest result was 0.406 or lower. For the five questions outside the guides’ scope, it was 0.808 or higher. Since 0.6 falls between those groups, I kept the starter value.

The cutoff alone cannot catch every question the guides don’t answer. For example, a question about a town in the guides might retrieve a relevant section even if that section lacks the specific answer. That’s why the prompt also tells the model to say when the retrieved text does not contain the answer.


| Question | In corpus? | Best distance |
|---|---|---|
| Does a bus run to Kestrelford on Sundays? | Yes | 0.286 |
| How much does it cost to climb the church tower in Kestrelford? | Yes | 0.406 |
| Can I get a taxi in Corry Vale without booking ahead? | Yes | 0.370 |
| What time do the pubs in Kestrelford stop serving food in the evening? | Yes | 0.165 |
| How long does the train from Brightwater to the regional hub take? | Yes | 0.238 |
| What is the capital of Mongolia? | No | 0.808 |
| How do I change the oil in a diesel engine? | No | 0.881 |
| Who won the 1994 World Cup? | No | 0.982 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.835 |
| How do I write a for loop in Rust? | No | 0.859 |

## How I Used AI

**1.** I asked Claude Code to replace the starter’s fixed-size chunker with one that follows the structure of the guides. Its first version made one chunk per section and split long sections by sentence with some overlap.

When I printed the chunks, I noticed a problem in the accessibility guide: some chunks started mid-sentence, and the paragraph breaks were gone. That made them hard to understand on their own. I asked Claude to keep whole paragraphs together, since each paragraph covers one town, and to split by sentence only when a paragraph is too long. I printed the chunks again to check that each one ended with a complete sentence.

**2.** `python app.py index` stopped partway through creating embeddings with exit code 137 and no error message. To investigate, I had Claude test batches of 8, 32, and 91 texts. The smaller batches worked, but the batch of 91 was killed. That pointed to a memory limit on my 8 GB machine.

Claude updated `store.py` to process 16 texts at a time. After that, indexing finished in about 13 seconds. Claude also drafted my acceptance criteria 4 and 5. Before keeping them, I checked their chunk sizes against the index results: the shortest was 201 characters and the longest was 678.


<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

`AI201_HYBRID` unset, `python run_eval.py --label before` (3 runs per question, caching off, 15 model calls), plus `python check_chunks.py before`. Raw logs: [results/run_2026-09-25_2350_before.md](results/run_2026-09-25_2350_before.md), [results/criteria_before.json](results/criteria_before.json) (per-run criterion 1/2/5 flags), [results/chunks_before.json](results/chunks_before.json).

I wrote `scorer.py` (criteria 1, 2, 5) and `check_chunks.py` (criterion 4) for this. Each cell is the number of the 5 questions that passed in that run. Criterion 3 and 4 are deterministic, so the same number is in all three columns.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Every chunk 200-700 chars, ends on a full sentence | all chunks | 91/91 | 91/91 | 91/91 | MET |
| 5. Cited file contains the expected phrase | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

How each is measured (all from `questions.py`'s `expects` phrase):
- **1:** the whitespace-normalised `expects` phrase appears in the text of at least one of the top-5 retrieved chunks.
- **2:** the answer text contains a `guide_*.md` filename.
- **5:** at least one filename the answer cites is a real corpus file whose full text contains `expects`.

**Real output.** Criterion 1, retrieval for "Does a bus run to Kestrelford on Sundays?" (`store.py::search`, from `results/criteria_before.json`):

```
guide_regional_transport.md#1, guide_kestrelford.md#1, guide_kestrelford.md#2, guide_kestrelford.md#6, guide_kestrelford.md#4
```
`expects` = "not at all" is in `guide_kestrelford.md#1` (rank 2). Rank 1 (`guide_regional_transport.md#1`) says "does not run on Sundays", so it answers the question but not in the `expects` wording.

Criterion 2 and 5, an answer as produced by `generate.py::answer_from_chunks`:

```
It costs £2 to climb the church tower in Kestrelford (from guide_kestrelford.md).
```
```
The train from Brightwater to the regional hub takes 50 minutes. This comes from *guide_brightwater.md* and *guide_regional_transport.md*.
```

Criterion 3, `run_eval.py::check_out_of_scope` (cutoff 0.6, `gate.py::check`):

```
  refused  (best distance 0.808)  What is the capital of Mongolia?
  refused  (best distance 0.881)  How do I change the oil in a diesel engine?
  refused  (best distance 0.982)  Who won the 1994 World Cup?
  refused  (best distance 0.835)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.859)  How do I write a for loop in Rust?
  -> gate refused 5 of 5
```

Criterion 4, `check_chunks.py` over `chunker.py::split_documents`:

```
91 chunks, min 201, max 678, 0 violating
```

Note: my first "before" attempt scored 0/15 because of a path bug in my own `scorer.py` (it looked in `documents/documents/`). I fixed the scorer, deleted that log, and re-ran; the answers themselves were fine. Two other attempts hit the free tier's 15-requests-per-minute limit and were rerun after waiting.

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer (4 of 5) | **MET** | 5 of 5 in all three runs. Retrieval is deterministic, so the three runs are identical; the closest call was the Sunday-bus question, where the `expects` phrase is in rank 2, not rank 1. |
| 2 | Every answer names a source (5 of 5) | **MET** | 15 of 15 answers cited a `guide_*.md` file. This is the only criterion that depends on the model varying run to run, and it did not vary. |
| 3 | Gate stops out-of-corpus questions (4 of 5) | **MET** | 5 of 5 refused; the closest out-of-corpus question was 0.808, 0.2 past the 0.6 cutoff. |
| 4 | Chunks 200-700 chars, end on a full sentence | **MET** | 91 of 91 chunks; shortest 201, longest 678, none ending mid-sentence. |
| 5 | Cited file contains the expected phrase (5 of 5) | **MET** | 15 of 15 answers cited at least one file containing the phrase. |

I did not change any target or add a revision to `criteria.md`: nothing was unmeasurable, and nothing was missed.

## Diagnoses

**Nothing was missed, so there is no failed stage to diagnose.** What I can do honestly is say where the targets were soft, and what my own probing found.

- **Criterion 1 is lenient.** "Any of the top 5" out of 91 chunks is easy when a question names one town, since the top 5 are usually all from that town's guide. It said nothing about rank or about junk in the other slots. Rank of the first answer chunk (`expects` phrase) was [2, 1, 1, 1, 1], and 3 of the 25 retrieved slots came from unrelated towns (`givens_mill#3`, `marchwood#1`, `thornby_wells#1`). That is a **retrieval-stage** weakness: dense embeddings match on meaning, so a chunk about another town's pub or train is "close enough" and takes a slot.
- **Criterion 3 was measured on the easy case only.** All five out-of-scope questions are about a different world (Mongolia, Rust). The failure the criterion itself worried about is a question on a topic the guides *do* cover but don't answer. I probed six such questions (not part of the scored set): the gate let all six through, at distances 0.366 to 0.439 against a 0.6 cutoff, so **the gate cannot catch that case at all** (**retrieval/gate stage**: a same-topic chunk is always close). The model's prompt then declined 3 of the 6 (pizza restaurant in Marchwood, ATM in Kestrelford, car rental in Corry Vale) and answered the other 3. I did not check those three against the guides, so I can't say if they were wrong.
- **Criterion 4 was nearly circular.** I took 200 and 700 from the lengths of the index I had just built (201 and 678), so it could hardly fail. If I tightened one, it would be this one, to a bound set before looking at the index.
- **Criteria 2 and 5** pass when a model cites two files (three answers cite both a town guide and the regional guide), which hides whether the *right* one was used.

## The Improvement

**What I changed:** Added hybrid retrieval to `store.py::search` (`_hybrid_rerank`). Dense results for the whole index are fused with a BM25 ranking of the same chunks using reciprocal rank fusion, and the top 5 are returned. Each chunk keeps its own dense distance so `gate.py` is untouched. It is switched on with `AI201_HYBRID=1`, so before and after use the same code and the same index, and the default is unchanged.

**Why I picked it:** It targets the retrieval-stage weakness above: dense-only retrieval lets same-topic chunks from other towns into the top 5 and ignores exact words that matter here ("Sunday", "£2", "8:30"); BM25 rewards those exact words.

### Run Log — After

`AI201_HYBRID=1 python run_eval.py --label after`. Raw logs: [results/run_2026-09-25_2354_after.md](results/run_2026-09-25_2354_after.md), [results/criteria_after.json](results/criteria_after.json), [results/chunks_after.json](results/chunks_after.json).

| Criterion | Target | Before (R1/R2/R3) | After (R1/R2/R3) | Verdict |
|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 / 5 / 5 | 5 / 5 / 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 / 5 / 5 | 5 / 5 / 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 / 5 / 5 | 5 / 5 / 5 | MET |
| 4. Chunk length and sentence ends | all chunks | 91 / 91 / 91 | 91 / 91 / 91 | MET |
| 5. Cited file contains expected phrase | 5 of 5 | 5 / 5 / 5 | 5 / 5 / 5 | MET |

Secondary retrieval measurements from the same runs (not criteria, just how I judged whether the fix did what I wanted):

| | Before | After |
|---|---|---|
| Rank of first chunk containing `expects` (5 questions) | 2, 1, 1, 1, 1 | 2, 1, 1, 1, 1 |
| Retrieved chunks from unrelated towns/topics (of 25) | 3 | 7 |
| Closest out-of-scope distance (gate margin) | 0.808 | 0.808 |
| Out-of-scope refused | 5 of 5 | 5 of 5 |

After, the Sunday-bus retrieval was `regional_transport#1, kestrelford#1, kestrelford#2, givens_mill#1, kestrelford#4`.

**Did it help?** No. The five criteria were already all MET, so they could not improve, and they didn't change. On the measure that mattered, it was slightly **worse**: the rank of the answer chunk did not move, and the number of off-topic chunks in the top 5 went from 3 to 7 (Givens Mill, Elder Ness, Pellew Sands, Walking, and a Brightwater chunk for a Kestrelford question). The reason is visible in the log: with only 91 short chunks, BM25 rewards any chunk sharing a common word like "the", "in", "Kestrelford", and fusing it in pushes a lexical near-miss above a semantically better dense hit. I would not ship it. I left it behind the `AI201_HYBRID` flag rather than deleting it so the result is reproducible; it is off by default. The gate margin was not affected.

I only ran the full evaluation once for the "after" state, so a small difference of one or two chunks could be noise; the direction (more junk, no better rank) is consistent across all five questions.

## What's Still Broken

- **Same-topic questions the guides don't answer still pass the gate.** The 0.6 cutoff separates "different world" from "this world" but not "answered" from "not answered". Six probe questions had distances of 0.37 to 0.44. Right now only the prompt in `generate.py` stops a wrong answer, and it declined only 3 of 6. Next I'd add a scored set of ~5 near-topic unanswerable questions to `questions.py`, and try either a tighter cutoff (which would risk refusing the real questions at 0.406) or a second check on whether the top chunk actually contains the asked-for fact.
- **Top-5 has off-topic chunks** even before my change (3 of 25). A fix I'd try next instead of BM25: filter or boost by the town named in the question, since the questions mostly name one.
- **The hybrid change isn't an improvement**, as measured above. I stopped after one attempt because the milestone asks for one measured fix and the measurement was already clear; further tuning of BM25 weights on five questions would be fitting to the test.
- **The scoring script is mine and simple.** The `expects` phrase check misses correct answers worded differently (the Sunday-bus rank-1 chunk), so criterion 1 could under-report.

## What I'd Do Differently

- **Criterion 1:** require the answer chunk in the **top 3** and count off-topic chunks, not just "somewhere in the top 5"; as written I could not have failed it on a five-town corpus.
- **Criterion 3:** score it on near-topic unanswerable questions as well, since those are the failures a real user hits. Five questions about Mongolia and Rust tested the easy half.
- **Criterion 4:** choose the length bounds *before* running the indexer. I took them from the index's own min and max, which nearly guaranteed a pass.
- **Criteria 2 and 5:** merge into one: "the answer cites the file the fact comes from and no file that doesn't contain it". Right now 2 says "any file" and 5 says "at least one", which allows a wrong extra citation.
- Write the scorer at the same time as the criteria; I only found the `expects` wording problem once I ran it.

## How I Used AI in Unit 2

I had Claude Code write `scorer.py`, `check_chunks.py` and the hybrid reranker, and run the evaluations. Claude's first scorer had a path bug that failed all 15 runs; I noticed 0/15 was implausible (the answers in the log were correct), had it fix the bug and re-run. I also had it probe the gate with near-topic questions that were not part of my original set. The verdicts and the decision not to change any targets are mine.
