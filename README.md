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

## Before the Change

I ran the evaluation three times with `AI201_HYBRID` off. Each run tested five questions. I also checked all 91 document chunks.

| Criterion | Target | Result | Verdict |
|---|---:|---:|---|
| 1. A retrieved chunk contains the expected answer | 4 of 5 questions | 5 of 5 in every run | Met |
| 2. Every answer names a source | 5 of 5 questions | 5 of 5 in every run | Met |
| 3. The gate refuses questions outside the guides | 4 of 5 questions | 5 of 5 in every run | Met |
| 4. Chunks are 200–700 characters and end with a full sentence | All chunks | 91 of 91 | Met |
| 5. A cited file contains the expected phrase | 5 of 5 questions | 5 of 5 in every run | Met |

For example, the answer about climbing the Kestrelford church tower said it costs £2 and cited `guide_kestrelford.md`. The gate also refused all five questions about subjects outside the guides.

**Before logs:** [Evaluation](results/run_2026-09-25_2350_before.md) · [Criteria results](results/criteria_before.json) · [Chunk results](results/chunks_before.json)

## What the Results Missed

All five criteria passed, but the tests revealed some limits:

- The retrieval test only required the answer to appear somewhere in the top five chunks. It did not check whether unrelated chunks also appeared.
- The gate refused clearly unrelated questions, such as questions about Mongolia or Rust. I also tried six questions about topics related to the guides but not clearly answered by them. The gate allowed all six through.
- The chunk length limits were chosen after I saw the chunk lengths, which made that test too easy to pass.
- An answer could cite an extra, incorrect file and still pass the source checks.

## The Change I Tried

I added an optional **hybrid search** mode to `store.py`. It combines the existing semantic search with BM25, which rewards matching words in the question and document. I hoped this would make details such as “Sunday” and “£2” easier to find.

The mode runs when `AI201_HYBRID=1`. It is off by default.

## After the Change

I ran the same evaluation with hybrid search on. All five criteria still passed, but retrieval did not improve.

| Retrieval measure | Before | After |
|---|---:|---:|
| Position of the first chunk with the expected phrase, across five questions | 2, 1, 1, 1, 1 | 2, 1, 1, 1, 1 |
| Unrelated chunks in the top five results, across all questions | 3 of 25 | 7 of 25 |
| Questions outside the guides refused by the gate | 5 of 5 | 5 of 5 |

**After logs:** [Evaluation](results/run_2026-09-25_2354_after.md) · [Criteria results](results/criteria_after.json) · [Chunk results](results/chunks_after.json)

**Conclusion:** Hybrid search did not help in this test. The expected answer chunks stayed in the same positions, while more unrelated chunks appeared. I left the feature off by default.

## What I Would Improve Next

1. Add questions that sound relevant to the guides but cannot be answered from them. These would give the gate a more useful test.
2. Check whether the town named in a question matches the town in a retrieved chunk.
3. Require the answer chunk to appear in the top three results and count unrelated results.
4. Require each citation to point to a file that supports the answer.
5. Set chunk length limits before building the index.

## How I Used AI

I used Claude Code to help me with some of my functions in the code and the hybrid search. The first scoring script had a file path bug, which I caught after checking the answers. I had it fix the bug and rerun the test. I reviewed the results and decided not to change the original targets.
