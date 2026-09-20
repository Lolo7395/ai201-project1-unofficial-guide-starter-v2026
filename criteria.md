# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
All five of my questions are single-fact lookups (a price, a time, a duration)
that live in one short section of one guide, but two of them (Sunday buses,
the Brightwater train) are also mentioned in the regional transport guide, so
near-duplicate chunks can crowd the top five. 4 of 5 leaves room for one such
crowding-out miss without accepting a retriever that fails a third of the time.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
Every chunk carries its guide title and source filename, and the generation
prompt tells the model to cite them, so a missing source is a prompt or
formatting failure, not a hard-question failure. Nothing about the setup
excuses one, so the target is 5 of 5, not 4. What would have to go wrong: the
model answering from a chunk without naming its file.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
When I set the cutoff in Milestone 4 there was a clean gap: my in-corpus
questions had best distances of 0.165-0.406 and the five out-of-scope ones
0.808-0.982. With a cutoff of 0.6 sitting in that gap I could have asked for
5 of 5, but the pre-written 4 of 5 stands because a borderline question (for
example "what's the weather in Brightwater?") would land near the cutoff and
I don't want the target to depend on that never happening.

---

## 4. Something about your chunks

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

Every chunk is at least 200 characters and none is longer than 700, and every
chunk ends on a complete sentence (no chunk cut mid-sentence at its end).

**Why this target:**

My guides are written in "## " sections of roughly 150-650 characters, each on
one topic. In Milestone 3 the smallest useful section (a "Where to stay" of
about 200 characters) was still a whole answer, so anything under 200 would be
a heading or fragment with no content, and anything over 700 would mean two
topics were glued together and diluting the embedding. Both bounds are
countable from `python app.py index`, which reports the shortest and longest
chunk (currently 201 and 678), and the sentence-end check is a one-line script.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->

The source named in the answer is the document that actually contains the
answer: for 5 of 5 test questions, at least one cited file is the one whose
text contains the `expects` phrase.

**Why this target:**

Criterion 2 only checks that a source is named, which a model could satisfy by
citing a plausible-sounding but wrong guide. Because the region's guides
overlap heavily (Kestrelford appears in its own guide, the transport guide,
the eating guide and the accessibility guide), attribution is the failure I
would most worry about, and it is the one that makes the guide trustworthy.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
