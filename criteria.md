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
All five questions ask for a simple fact, like a price, time, or trip length, and the answers are in one short section of the guide. 
Two topics—Sunday buses and the Brightwater train—also appear in the regional transport guide. 
That means similar passages could fill the top five search results and push out one answer.
 A **4 out of 5** target allows for one miss, while still expecting the retriever to find most of the answers.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
Every chunk includes the guide title and filename, and the prompt asks the model to cite them. 
So if an answer is missing a source, the issue is with how the model followed the prompt or formatted
its answer—not with how difficult the question was. The target should be **5 out of 5**. 
 A miss would mean the model used a chunk to answer but forgot to name its source file.


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
When I set the cutoff in Milestone 4, there was a clear gap in the results. Questions covered by the guides had distances from 0.165 to 0.406, while the five questions outside their scope had distances from 0.808 to 0.982. The 0.6 cutoff falls between those ranges, so it handled all five test questions correctly. I’m keeping the original **4 out of 5** target, though, because a borderline question like “What’s the weather in Brightwater?” might fall close to the cutoff. I don’t want the target to assume every future question will be as clear-cut.


---

## 4. Something about your chunks

Every chunk is at least 200 characters and none is longer than 700, and every
chunk ends on a complete sentence (no chunk cut mid-sentence at its end).

**Why this target:**

My guides are divided into `##` sections, with each section covering one topic. Most are about 150–650 characters long. In Milestone 3, the shortest useful section was a “Where to stay” section of about 200 characters, and it still contained a complete answer. A chunk shorter than 200 characters would likely be just a heading or fragment. A chunk longer than 700 might combine two topics, making it harder for the retriever to find the right information.

I can check the lengths by running `python app.py index`, which reports the shortest and longest chunks—currently 201 and 678 characters. A short script can check whether each chunk ends with a complete sentence.


---

## 5. Your choice

For all five test questions, the answer should cite a file that actually contains the expected information. l checked this by making sure at least one cited file contains the question’s `expects` phrase.

**Why this target:**

Criterion 2 only checks whether the answer names a source. The model could pass that check even if it cites the wrong guide. This matters because the guides overlap: Kestrelford, for example, appears in the town guide, transport guide, eating guide, and accessibility guide. I’d be most concerned about citing the wrong source, since readers need to be able to check where an answer came from.

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
