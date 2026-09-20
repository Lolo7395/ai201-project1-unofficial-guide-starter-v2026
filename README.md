# The Unofficial Guide

Lorraine Mureya — corpus: `city_guides`.

---

# Unit 1

## What This Does

The Unofficial Guide is a retrieval-augmented question-answering tool over the
`city_guides` corpus: fourteen short travel guides to a fictional region
(Brightwater, Kestrelford, Corry Vale, Halden Bay, Marchwood and others, plus
region-wide guides on transport, eating, accessibility, walking and seasons).
You ask practical questions such as "Does a bus run to Kestrelford on
Sundays?" and it retrieves the closest guide sections from a Chroma vector
store, and answers using only that text, naming the source guide. If nothing
in the guides is close enough to the question, a relevance gate refuses
instead of guessing. Run it with `python app.py index` then
`python app.py ask "..."`.

## Chunking Strategy

**Chunk size:** one `## ` section per chunk, capped at 650 characters
(`CHUNK_SIZE`), with sections under 180 characters (`MIN_CHUNK_SIZE`) merged
into the next one. Actual result: 91 chunks, 201 to 678 characters, 327 on
average.
**Overlap:** 90 characters, used only when a single paragraph is longer than
the cap and has to be split at a sentence end. Paragraph-aligned splits carry
no overlap.

When I read the guides in Milestone 1, every one turned out to be a few
`## ` sections (Getting there, Where to stay, When to go...) of roughly
150-650 characters, each one a single topic. The answer to a question like
"how much to climb the tower" is one sentence inside one such section, so
cutting on a fixed character count (the starter's 800/120) would slice through
sections and glue unrelated topics together, while splitting on sections keeps
each fact with its context. Each chunk is prefixed with
`<guide title> - <section heading>` because a sentence like "There is no local
bus service" is meaningless without knowing which town, and the prefix also
puts the town name into the embedding.

I changed my mind once. My first version split over-long sections on
sentences with a character overlap; the accessibility guide came out as chunks
starting mid-sentence ("market are both step-free") and lost its paragraph
breaks. Its paragraphs are one town each, so I changed the splitter to pack
whole paragraphs first and only fall back to sentence splits (with whole-sentence
overlap) for a paragraph that alone exceeds the cap.

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

**My relevance cutoff:** `THRESHOLD = 0.6` in `config.py`. Distances are lower
= closer. My five in-corpus questions all had a best distance of 0.406 or
less, and the five out-of-scope questions all had 0.808 or more, so there is a
gap of about 0.4 and 0.6 sits roughly in the middle. I did not have to tune it
tightly; I kept the starter value because the measurements supported it. A
question can still slip through the gate if it is about a town in the guides
but asks something they do not say, which is why the prompt also tells the
model to refuse when the chunks do not contain the answer.

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

**1.** I asked Claude Code to replace the starter's fixed-size chunker with one
built for the guides. It wrote a section-per-chunk splitter with a
sentence-level overlap for long sections. When I printed the chunks, the
accessibility guide was chopped mid-sentence and had lost its paragraph
breaks, so the chunk did not stand on its own. I had Claude change the
splitter to keep whole paragraphs together (each is one town) and only split
on sentences for a paragraph that is longer than the cap, then re-printed the
chunks to check every one now ends on a complete sentence.

**2.** `python app.py index` died with exit code 137 and no error message
partway through embedding. Claude narrowed it down by embedding batches of
8, 32 and 91 texts directly: 8 and 32 worked and 91 was killed, which pointed
to memory use on my 8 GB machine rather than a bad model download. The fix was
to embed in batches of 16 in `store.py`; indexing then completed in about 13
seconds. I also had Claude draft my acceptance criteria 4 and 5; I checked the
numbers in them against what the index reported (shortest chunk 201,
longest 678) before keeping them.

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

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
