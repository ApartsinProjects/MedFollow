# Anticipated Reviewer Concerns and Prepared Responses

Internal preparation document for the MedFollow JBI submission. Lists
the most likely reviewer concerns based on the paper's current scope
and evidence base, together with the response we would offer in a
revision. **Not for submission.**

The principal vulnerability of the paper is that all evaluation is
synthetic. Most other concerns flow from that; we should not minimize
it but we should be ready with concrete answers to each variant.

---

## Concern 1 (almost certain). "The evaluation is synthetic-only."

**Likely framing.** *"While the proposed architecture is technically
reasonable, the paper's evidence rests entirely on a synthetically
generated corpus. The authors acknowledge this, but it is unclear that
the reported gains transfer to real EHR documentation, where clinician
phrasing variability, document structure, and instruction ambiguity
are far higher than what the generator produces. I would expect at
least a small clinician-annotated real-note evaluation before the
methodological claims can be supported."*

**Our response.**

1. We agree this is the principal limitation and have stated so
   explicitly in the Abstract (Conclusion paragraph), in the Discussion
   (Section 5, "Synthetic-data caveats"), and in Limitations (5.1).
2. The paper's contribution is *methodological*, not *empirical
   transferability*: it isolates a specific reliability failure of
   end-to-end generative extraction (calendar arithmetic) and
   demonstrates that a decomposed architecture removes it under a
   controlled benchmark. The decomposition argument is generic; the
   numbers are specific to this benchmark.
3. The corpus was deliberately designed with stress factors (multi-
   action notes, historical-time distractors, shorthand temporal
   forms, proximity traps, six plan-section variants, ten style-
   feature axes, 549 distinct temporal-expression surface forms) that
   target the failure modes most likely to differ from generator-
   smoothed text. Section 3.2 documents this.
4. We have begun assembling a real-note evaluation set drawn from
   MTSamples (Apache-2.0, ~600 candidate outpatient/discharge/SOAP
   notes after filtering) and are pursuing PhysioNet credentialing
   for a MIMIC-IV-Note discharge-summary subset. We propose to add
   results on this real-note set as supplementary material in
   revision, framed as an out-of-distribution sanity check rather
   than as the headline evaluation.
5. We note that the in-text follow-up density of the high-yield
   MTSamples specialties (69% Discharge Summary, 49% SOAP/Progress
   Notes, 40% Emergency Room, 32% General Medicine) is comparable to
   our synthetic corpus's 75% non-zero-action note share, which gives
   reason to believe the dataset distributions overlap meaningfully.

If the editor allows, we would prefer to add the real-note appendix
in a revision rather than withdraw and re-submit; the methodological
contribution stands on its own and does not depend on the new data.

---

## Concern 2 (very likely). "Where are the ablations?"

**Likely framing.** *"The paper attributes the headline gain to the
deterministic-normalization design but does not isolate this. The
right experiments are: (a) hold the BioBERT spans+linker fixed and
let the LLM produce the date instead of `dateparser`; (b) hold the
LLM extraction fixed and pass its time-phrase output to `dateparser`.
Without these the causal claim is unsupported."*

**Our response.**

1. We agree these ablations are the most informative next experiments
   and they are explicitly listed as planned next-version work in
   Section 5.1.
2. We can already provide a partial qualitative argument from data
   already in the repository: the LLaMA-3 8B fine-tuned baseline
   reaches perfect action-span F1 (1.000 [1.000, 1.000]) but does not
   improve on time-span F1 or date metrics over zero-shot ChatGPT
   (Section 5, "Fine-tuning did not close the temporal gap"). This
   indicates that the fine-tuned model can recognize *what* the action
   is but cannot reliably *compute the date*. Replacing its date
   output with deterministic normalization on its own predicted phrase
   would, by construction, reduce date error to whatever
   `dateparser` produces, which is the headline number.
3. We can compute the (b) ablation from the existing eval (per-note
   prediction reconstruction) once the BioBERT and LLaMA checkpoints
   are restored from the original training environment; this is a
   small additional run on the existing test split and we propose to
   report it in revision as Table 3.

We commit to including ablations (b) and (a) in the first revision.

---

## Concern 3 (likely). "The baselines are too weak for a strong claim."

**Likely framing.** *"GPT-4o-mini zero-shot and LLaMA-3 8B with a
small LoRA are reasonable starting baselines, but the strong claim of
'hybrid system outperforms LLMs' would benefit from at least: (i) a
larger LLM (GPT-4 / GPT-5 / Claude / a 70B-class fine-tune); (ii)
constrained decoding such as outlines/JSON-schema; (iii) tool use
(letting the LLM call a date library); (iv) retrieval augmentation."*

**Our response.**

1. We do not claim our system outperforms *all* generative approaches.
   The paper's claim is narrower (Section 5, "Scope of the LLM
   comparison"): on this benchmark, our hybrid system materially
   outperforms two reasonable baselines on strict action-date
   correctness and date arithmetic, with non-overlapping 95% CIs.
2. The methodological argument is that the calendar-arithmetic failure
   mode is *systematic* in unconstrained generation. A larger LLM
   would likely close some of the gap; a tool-using LLM that delegates
   the date calculation to a calculator would, by definition, recover
   most of the deterministic-normalizer's advantage, which is
   precisely the architectural pattern we advocate.
3. We will add stronger-baseline comparisons (GPT-4o, GPT-5,
   instructor-XL, Claude Sonnet) to a revision as supplementary
   results, contingent on API budget and the editor's preference. The
   paper's contribution is the architectural pattern, not the specific
   horse-race numbers.

---

## Concern 4 (likely). "The corpus may be biased toward the system's strengths."

**Likely framing.** *"The dataset was generated by `gpt-4o-mini`, the
same model family used as one of the baselines. The proposed BioBERT
hybrid was trained on this generator's output. There is a real risk
that the gap reported is partly explained by overfitting to generator
artifacts that the LLM baselines do not capture in the same way."*

**Our response.**

1. The risk is real. We mitigate it through the ten style-feature
   axes, six plan-section variants, and 549 distinct temporal-
   expression surface forms (Section 3.2, Figures 3 and 4). The most
   frequent temporal expression accounts for only twelve mentions in
   2,028 gold mentions; this is more diverse than a generator that
   was producing repetitive output would yield.
2. The zero-shot ChatGPT baseline (`gpt-4o-mini`) is the *same model
   family* as the generator, and yet it achieves only 0.827 F1 on
   action-date and 5.07-day MAE. If the corpus were significantly
   biased to be solvable by `gpt-4o-mini`, we would expect this
   baseline to be the strongest performer, not the middle one.
3. The headline gap (1-day vs 5-11 day MAE) is too large to be
   explained by stylistic overfitting alone: the deterministic
   normalizer is the only component that systematically computes
   dates from phrases, and it does not learn from the corpus at all.
4. The real-note evaluation in revision (Concern 1) is the proper
   answer to this concern.

---

## Concern 5 (medium). "Single split, no multi-seed training."

**Likely framing.** *"The paper reports one held-out split with seed
42 and Wilson / bootstrap CIs computed at evaluation time. There is
no across-seed variance estimate from training, which is the more
standard way to report uncertainty in deep learning."*

**Our response.**

1. The Wilson CIs on proportion metrics and the 10,000-replicate
   bootstrap CIs on F1 metrics are computed at the note level (after
   per-note rerun in revision; currently at the instance level on
   reconstructed TP/FP/FN counts). These characterize *evaluation*
   sampling uncertainty, which is the most common source of noise in
   reported headline numbers.
2. Multi-seed training and multi-fold splits are explicitly listed as
   planned next-version work in Section 5.1.
3. We commit to adding 5-seed BioBERT training results as
   supplementary material in revision, using the same hyperparameters
   reported in Section 3.3.

---

## Concern 6 (medium). "Why not a stronger / cleaner taxonomy of action types?"

**Likely framing.** *"The 28-action closed set covers procedures,
imaging, labs, and consults but excludes medications, conditional
follow-up ('return if symptoms worsen'), and ambiguous instructions.
This narrows the practical relevance."*

**Our response.**

1. We acknowledge this in Limitations (Section 5.1, "Limited action
   ontology"). The closed set was chosen for tractability of the
   exact-offset evaluation; medication changes especially require a
   different schema (drug + dose + frequency + duration).
2. Extending to medications and conditional follow-up is planned as
   future work; the linker architecture is unchanged, only the action
   schema and the evaluation conventions need extending.

---

## Concern 7 (lower). "References are missing X."

**Likely framing.** Reviewer suggests adding specific recent papers,
e.g.: more recent clinical LLM benchmarks; specific work on outpatient
follow-up extraction; the latest BERT-family clinical models; the
TIMEX3 / TimeML lineage explicitly cited.

**Our response.**

We will gladly add any specific reference the reviewer recommends. The
current 22-reference list covers clinical IE foundations (cTAKES,
clinical IE review), temporal extraction (i2b2 challenge, THYME,
Clinical TempEval, HeidelTime, SUTime, BERT-based clinical temporal
relation extraction), domain-specific encoders (BERT, BioBERT,
ClinicalBERT, PubMedBERT, GatorTron), span-relation modeling (SpERT,
biaffine attention), LLM clinical extraction (Agrawal 2022, Huang
2024, Wornow 2023, Hu 2024), and synthetic clinical data (Kweon 2024,
Loni 2025). We are open to adding specific recent work the reviewer
flags.

---

## Concern 8 (lower). "What about the audit-flagged 26 notes?"

**Likely framing.** *"The corpus contains 26 notes (1.3%) carrying
validation flags. Two are excluded from the test set. How are these
handled in training? Could they be a source of noise in the reported
metrics?"*

**Our response.**

The 26 flagged notes are retained in the released data with their
flag codes (e.g., `plan_header_not_exactly_once`,
`extra_closed_set_action_in_plan`) for transparency. They are not
excluded from training; the BioBERT hybrid is trained on the full
1,600-note training split including any flagged notes that fall in
the train or validation portion. The two test-split flagged notes are
excluded from evaluation because their annotations are uncertain.
Including or excluding them in training would not materially affect
the conclusions because the flag rate is well under 2% of the corpus.

---

## Concern 9 (lower). "The proposed pipeline relies on `dateparser`'s English-locale grammar."

**Likely framing.** *"The deterministic normalizer is a single-language
library with limited coverage of clinical shorthand. What happens
when notes contain phrases the library does not parse?"*

**Our response.**

`dateparser` is the only locale-dependent component in the pipeline.
For unparsable phrases the normalizer returns `None`; these become
recall losses on date metrics but never produce wrong dates. We have
not measured the parser miss rate explicitly on this corpus and will
add it to a revision as Table 4 (per-stratum analysis), broken down
by canonical phrases vs shorthand vs less-common forms. The
architecture is parser-agnostic; HeidelTime, SUTime, or a custom
clinical-shorthand grammar could be substituted with no change to
the neural components.

---

## Concern 10 (lower). "Statistical-significance argument is via CI non-overlap."

**Likely framing.** *"The paper uses non-overlap of 95% confidence
intervals as a stand-in for a significance test. This is more
conservative than a paired test but does not give a p-value or effect
size in the conventional sense."*

**Our response.**

CI non-overlap is a conservative test (it implies the corresponding
two-sided z-test rejects at p < 0.005, not 0.05; the paper claims
p < 0.05 only). We will add per-note paired McNemar tests on
action-date correctness and per-note Wilcoxon signed-rank tests on
absolute date error in revision once per-note predictions are
restored, as supplementary Table S2.

---

## Likely-decision summary

If the manuscript is sent for review, we anticipate:

- **Decision:** *major revision*, with a request for (a) real-note
  evaluation, (b) the two key ablations (date normalization in
  isolation; linker variants), (c) multi-seed CIs, and (d) per-
  stratum analysis.
- **Path to acceptance:** all of (a)-(d) are tractable from the
  existing codebase and a modest amount of additional compute /
  annotation effort. Real-note evaluation on 50-100 MTSamples notes
  is the riskiest item; the rest are bookkeeping.
- **What would warrant rejection:** an editor concluding that the
  contribution is too narrow without real-note results; or that the
  comparison should include constrained-decoding LLMs as the primary
  baselines rather than as an ablation. Either is a paper-shape
  judgment we should be ready to argue against.

We should plan revision capacity of roughly 1-2 months of part-time
work to address Concerns 1-5 fully, plus a small annotation effort
for Concern 1.
