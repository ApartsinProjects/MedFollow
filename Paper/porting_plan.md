# Porting Plan: Aligning MedFollow Paper with Updated Repo + Michal's Report

Source materials reviewed:

- `newrepo/` — Michal's updated repo at https://github.com/michallaufer/Clinical-Follow-up-Extraction
- `newrepo/artifacts/followup_extraction_paper.docx` — Michal's updated paper (189 paragraphs, 8 tables, 5 figures, 11 numbered sections plus 3 appendices)
- `newrepo/results/biobert_ner_token_report_{seen,oov}.csv` — token-level NER reports
- `newrepo/results/seen_vs_oov_comparison.png` — comparison figure
- `newrepo/src/data_utils.py` — disjoint-action split logic
- `newrepo/src/evaluate.py` — note-level bootstrap CIs
- `newrepo/src/time_utils.py` — `period_text -> days_offset` normalization
- `newrepo/src/ontology.py` — 28-canonical-action alias index

Current paper: `Paper/index.html`, `Paper/MedFollow_JBI_submission.docx` (DOCX-side audit clean 24/24, JBI-compliant body shape).

## Headline divergences

The new repo + Michal's paper are **the same architecture and corpus** as ours, but with three substantial methodological changes that materially change the headline numbers:

| Aspect | Current paper | Michal's paper | Impact |
|---|---|---|---|
| **Split** | Random 80/10/10 (1,600/200/200) seed 42 | **Action-disjoint Seen/OOV split**: 901 train / 100 seen-val / 178 OOV-val / 259 seen-test / 259 OOV-test (18 seen action types, 4 + 6 held-out) | Tests **generalization to action types never seen during training**, much stronger evidence |
| **Output schema** | `{action, period_text, period_date}` (ISO date) | `{action, days_offset}` (integer days relative to visit date) | Cleaner; decouples ground truth from wall-clock |
| **Bootstrap** | Instance-level over reconstructed (TP, FP, FN) | **Note-level resampling** (1,000 iterations) | Standard methodology; tighter CIs |

The empirical story tightens dramatically:

| Metric | Our paper | Michal's seen-test | Michal's OOV-test |
|---|---|---|---|
| BioBERT Pair F1 | **0.980 [0.964, 0.992]** | **0.997 [0.990, 1.000]** | **0.986 [0.972, 0.997]** |
| LLaMA Pair F1 | 0.806 [0.762, 0.847] | 0.510 [0.455, 0.562] | 0.566 [0.512, 0.625] |
| GPT-4o-mini Pair F1 | 0.827 [0.783, 0.864] | 0.528 [0.471, 0.581] | 0.532 [0.474, 0.590] |
| BioBERT MAE | 0.53 days | **0.00 days** | **0.00 days** |
| LLaMA MAE | 10.88 days | 21.31 days | 6.25 days |
| GPT-4o-mini MAE | 5.07 days | 23.65 days | 10.36 days |

The new numbers tell a much stronger story: **end-to-end LLM extraction fails on full-pair reconstruction even when action labels are correct** (LLaMA gets action F1 0.992 but Pair F1 0.510). This is the central claim the paper should make. Our current paper underplays this gap.

## Plan: 11 phases

### Phase 1. Naming and schema unification (1-2 hr)

Adopt the formal IE framing from Michal's paper. Global find-and-replace across `Paper/index.html`:

| Current term | New term |
|---|---|
| "action span" | TestSpecification entity |
| "time span" | TimeSpecification entity |
| "action-time linker" | ScheduledFor relation |
| "linker" | relation extractor |
| `B-ACT` / `I-ACT` BIO tags | `B-TEST` / `I-TEST` |
| `period_date` (output field) | `days_offset` |
| "Action F1" | TestSpecification F1 |
| "Time F1" | TimeSpecification Offset F1 |
| "Action-Date F1" | Test-Time Pair F1 |
| "Date MAE" | Time offset MAE (days) |

Keep "Action" only where it refers to the canonical label string (still 28 named actions).

### Phase 2. Split methodology rewrite (Section 3.2) (1 hr)

Replace the 80/10/10 random-split paragraph with the disjoint-action design:
- 28 canonical action types partitioned by `numpy` shuffle (seed 123) into 18 train / 4 OOV-val / 6 OOV-test types.
- A note is assigned to a split iff **all** its actions belong to the split's allowed action set.
- Additional held-out **seen-test** set (259 notes whose action types are in the train set) for in-distribution comparison.
- Final split: 901 train / 100 seen-val / 178 OOV-val / 259 seen-test / 259 OOV-test.

Replace Table 1 with a new combined dataset+split table.

### Phase 3. Methods updates (Section 3.3-3.6) (2-3 hr)

- Add **ScheduledFor relation** to the formal task definition (§3.1) as a first-class output.
- Update §3.3 (architecture): rename heads to "TEST/TIME entity extractor" + "ScheduledFor relation extractor". Keep the math the same.
- Update §3.4 (baselines): same content, but baseline output schema becomes `{action, period_date}` from the LLM, post-processed to `days_offset` for evaluation (matches Michal's Table 4).
- Update §3.5 (metrics): three set-level F1 metrics on canonical labels and integer offsets, plus MAE. Drop "exact date accuracy on matched actions" — superseded by Time-Offset F1.
- Update §3.6 (statistical analysis): note-level bootstrap (1,000 iterations, seed 123) instead of instance-level reconstruction. Wilson on proportions stays.

### Phase 4. Results section rewrite (Section 4) (2 hr)

- Replace Table 2 with Michal's Table 5 verbatim (6 rows × 6 cols: model × split × 3 F1s × MAE with 95% CIs).
- Update the interpretation paragraph: lead with the **action-recognition-vs-pair-reconstruction gap** for LLMs (LLaMA Action F1 0.992 but Pair F1 0.510 — generative models can name the action but cannot reliably reconstruct the full schedule).
- Replace Figure 5 (current grouped-bar comparison) with a new figure showing the seen vs OOV comparison panel. Use Michal's image2.png or regenerate.
- Replace Figure 6 (MAE) with a new MAE-by-split figure.

### Phase 5. Error Analysis (new subsection) (1-2 hr)

Add §4.x **Error Analysis** as a subsection of Results:
- Qualitative error-pattern table (Michal's Table 6, 6 rows × 4 cols).
- Five worked LLaMA/GPT failure examples from Michal's Table 7 (one per error pattern: abbreviation misinterpretation, severe temporal parsing, calendar/week-boundary, year-boundary hallucination, phrase interpretation, small arithmetic mismatch).
- Cross-link to our existing MTSamples top-20 coverage analysis as an additional realism check; the qualitative gap pattern matches.

### Phase 6. Discussion update (Section 5) (1 hr)

- Rename "Why decomposition wins" → "Auditability of the structured pipeline". Same argument but tighter, with Michal's framing (ScheduledFor relation is inspectable; direct generation is opaque).
- Strengthen "Fine-tuning did not close the temporal gap": the LLaMA Pair F1 of 0.510 on seen actions despite being fine-tuned on 901 notes from those same action types is direct evidence.
- Update §5.1 limitations: drop the "single split" caveat (we now have seen + OOV); keep the synthetic-only, ontology-coverage, dateparser-coverage, and no-workflow-validation items. Add the MTSamples 40% closed-set finding as an empirical-anchor sentence.

### Phase 7. Figure budget enforcement (1 hr)

JBI cap is 8 figures + tables. Current state if we just merge:
- 5 figures from Michal (system overview, generation pipeline, seen-vs-OOV comparison, plus 2 more)
- Our existing 6 figures (pipeline, composition, vocab distributions, stress factors, model-comparison-CI, MAE)
- 8 tables from Michal vs our 2

Final selection (8 total = 6 figures + 2 tables, at cap):
1. Figure 1: System overview (keep our redesigned pipeline.svg; matches Michal's Figure 1 in spirit, ours is cleaner)
2. Figure 2: Dataset composition (keep ours; Michal has no equivalent)
3. Figure 3: Vocabulary distributions (keep ours)
4. Figure 4: Stress-factor coverage (keep ours)
5. Figure 5: Seen vs OOV model-comparison F1 (regenerate with Michal's numbers + CIs; merge with current model-comparison-with-ci.png)
6. Figure 6: Time offset MAE by model and split (regenerate)
7. Table 1: Benchmark specification (merge our Table 1 + Michal's Table 1 into one)
8. Table 2: Seen + OOV results with 95% CIs (Michal's Table 5)

Drop from current state: stress-factor figure may need to merge into Figure 2 (composition) to free a slot.

Tables we lose by the cap: Michal's Table 2 (diversity axes), Table 3 (split details), Table 4 (model setup), Table 6 (error profile), Table 7 (error examples), Table 8 (LLaMA hyperparameters). These move to **Supplementary** materials.

### Phase 8. Appendices → Supplementary (1 hr)

Michal's body has three appendices (GPT prompt, LLaMA hyperparameters, BioBERT NER diagnostics). JBI does not number appendices into the body word/figure cap, but for the cleanest submission move them all into the supplementary zip as separate markdown documents. Keep one-sentence pointers in the body.

### Phase 9. References (1 hr)

Michal's bibliography uses a different numbering and includes references our paper doesn't (e.g., the structured-IE-with-LLMs paper at [11]). Need to:
- Diff Michal's references against our current 22-entry Vancouver bibliography.
- Add any new ones, drop any unused.
- Re-number throughout.
- Verify all DOIs/URLs.

### Phase 10. Abstract + Statement of Significance update (30 min)

- Rewrite abstract around the new headline numbers (Pair F1 0.997/0.986 vs 0.510/0.566).
- Adjust Statement of Significance "What this Paper Adds" with the new claim shape.
- Verify ≤300 words on abstract; ≤150 on Statement of Significance.

### Phase 11. Build + re-audit (30 min)

- Run `python Paper/scripts/build_docx.py --audit` to regenerate the JBI DOCX.
- Verify 24/24 PASS / 0 ISSUES.
- Rebuild supplementary zip with new contents (appendices added).
- Commit + push to GitHub Pages.

## Order of work (recommended)

Do **Phase 1 → 2 → 3 → 4 → 5** first as a coherent block. Phase 1-3 are mechanical renaming/restructure; phase 4-5 are the empirical update. Stop here; the paper at this point is **already publishable-grade**.

Then do **Phase 7 → 8 → 9 → 10 → 11** as the JBI-cap and final-polish pass.

Phase 6 (Discussion) can be interleaved with Phase 4-5 since it depends on the new numbers.

**Estimated total wall-clock:** 12-16 hours of focused work, mostly mechanical once decisions are made.

## What to use from Michal's docx directly

| Asset | Action |
|---|---|
| `image1.png` (2 MB) | Likely the system-overview figure; compare with our pipeline.svg. Probably keep ours. |
| `image2.png` (512 KB) | Probably the data-generation pipeline. Could be useful but we'd need to redraw cleanly. |
| `image3.png`, `image4.png`, `image5.png` (~80 KB each) | Likely the seen-vs-OOV bar charts. Re-render in matplotlib for editability. |
| Tables 5, 6, 7 | Verbatim text for results + error-analysis sections. |
| Table 8 (LLaMA hyperparameters) | Verbatim into Supplementary Appendix B. |
| Section 4.1 prose (synthetic generation procedure) | Tighter and more detailed than ours; consider porting. |
| Appendix A prompt template | Verbatim into Supplementary. |

## What we keep from current paper

- JBI body-shape (1 Intro / 2 Related Work / 3 Methods / 4 Results / 5 Discussion / 6 Conclusion). Michal's 11-section structure does **not** satisfy JBI's mandated shape; we must keep ours.
- Statement of Significance box (Michal's has none).
- All 7 post-Conclusion declaration blocks (CRediT, COI, Funding, Ethics, Data availability, AI use, Acknowledgements).
- Elsevier Vancouver reference formatting.
- Justified text + display-math centering CSS.
- Our `Paper/scripts/build_docx.py` build pipeline.
- Our redesigned Figure 1 (pipeline.svg) — it's cleaner than Michal's.
- Our MTSamples top-20 realism check as a Limitations-section sentence (Michal's paper doesn't have this — it's our unique contribution).

## Open questions for you

1. **Can you confirm Michal's seen/OOV numbers reproduce?** I have not re-run inference against the trained checkpoints — those are still on Drive. If we adopt Michal's results table verbatim and they later turn out to disagree with what `main.py` produces, that's a problem at proof stage. Quick sanity check: can you run `python main.py` once and confirm Table 5 reproduces?
2. **Do you want the Section 8 Error Analysis as a top-level section, or as Section 4.x subsection within Results?** JBI's fixed shape strongly prefers the latter (subsection of Results). Michal made it top-level.
3. **Drop or keep MTSamples top-20 work?** It's our unique addition. Recommend: keep as one paragraph in §5.1 Limitations (as "realism-check evidence from real transcribed notes") and as a supplementary appendix.
4. **Pin the citation title.** Should be one of the two:
   - "Reliable Follow-Up Action and Date Extraction from Clinical Notes: A Hybrid Neural-Symbolic Approach" (our current title)
   - "Reliable Extraction of Clinical Follow-Up Instructions as Structured Information Extraction" (Michal's title)
   - Or a merge. Michal's is closer to the IE community; ours is more direct. I'd suggest merging to **"Reliable Extraction of Clinical Follow-Up Instructions as Structured Information Extraction: A Hybrid Neural-Symbolic Pipeline"** — keeps both framings.

Once these four are settled I'll execute the plan top to bottom in one continuous pass.
