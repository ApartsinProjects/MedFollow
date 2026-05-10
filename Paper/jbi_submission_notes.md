# JBI Submission Notes: Hybrid NLP for Follow-Up Extraction

Research compiled 2026-05-10 against the live Elsevier "Guide for Authors" for the
Journal of Biomedical Informatics (JBI), ISSN 1532-0464. Primary source URL (now
redirects to ScienceDirect):

- Guide for Authors: https://www.sciencedirect.com/journal/journal-of-biomedical-informatics/publish/guide-for-authors
- About / scope: https://www.sciencedirect.com/science/journal/15320464/publish/about-the-journal
- Submission system: https://www.editorialmanager.com/jbi/default.aspx

JBI self-describes as "the premier methodology journal in the field of biomedical
informatics" (impact factor 4.5, CiteScore 10.2; Open Access APC USD 3,530).

---

## 1. Article-Type Recommendation for Our Paper

Our manuscript is a methods-plus-dataset-plus-comparative-evaluation paper on a
hybrid neural-symbolic system for follow-up instruction extraction from clinical
notes, with synthetic-only evaluation against LLM baselines.

JBI accepts the following submission categories (from the Guide for Authors):

| Category | When to use | Editorial gating |
|---|---|---|
| **Original Research** ("Research Paper" in EM) | Novel methodology-driven systems | None; standard submission |
| Methodological Review ("Review article") | Systematic summaries of method approaches | None |
| Special Communication | "Generalizable lessons from applying existing methods" | Requires editor pre-approval |
| Commentary | Discussion of published work / focus areas | Requires editor discussion beforehand |
| Letter to the Editor ("Correspondence") | Comments on previously published papers | None |
| Book Review / Editorial | Invitation only | n/a |

**Recommendation: submit as Original Research (Research Paper).** The work
introduces a new task formulation, a novel hybrid architecture, a new synthetic
corpus, and a comparative evaluation. It satisfies the "novel methodology-driven
system" framing JBI prefers. Methodological Review does not fit (we are not
summarizing a body of work) and Special Communication would understate the
methodological contribution.

Universal length envelope (must hold for Original Research):

- Structured abstract: "<=300 words"
- Body manuscript: "<=6000 words"
- Total figures and tables: "<=8"

Our current draft has 6 figures and 2 tables (8 total = at the cap). Body word
count needs to be measured; the current HTML has 11 body sections plus references,
so trimming will likely be required.

---

## 2. Mandatory Structural Changes vs. Our Current Draft

Current draft section structure (from `Paper/index.html`):

```
Abstract (Background / Methods / Results / Conclusions)
1. Introduction
  - Contributions box
2. Related Work (2.1 - 2.7)
3. Task Definition
4. Dataset (4.1 - 4.4)
5. Method (5.1 - 5.5)
6. Experiments (6.1 - 6.3)
7. Discussion
8. Limitations and Future Work
9. Ethics and Privacy
10. Reproducibility
11. Conclusion
References (numbered, anchor-linked)
```

JBI required body structure (verbatim from Guide for Authors):
> "Introduction, Related Work, Methods, Results, Discussion, and Conclusion;
> with a total of <=6000 words"

### Required structural edits

1. **Abstract headings must be Objective / Methods / Results / Conclusion.**
   Our draft uses "Background / Methods / Results / Conclusions". Rename
   "Background" to "Objective" and reframe its content to lead with the
   research question and aim, not the motivating prose. Rename "Conclusions"
   (plural) to "Conclusion" (singular) for consistency with the guide.

2. **Add a "Statement of Significance" table inside the Introduction.**
   The Guide for Authors mandates a 150-word-or-less table with these exact
   sub-headings (quoted from the guide):
   - "Problem or Issue"
   - "What is Already Known"
   - "What this Paper Adds"
   - "Who would benefit from the new knowledge in this paper"

   Per policy: it "should also be part of the Introduction section of the
   paper" (i.e., end of the Introduction section in the body). It is rendered
   as a small boxed table.

3. **Merge "Task Definition", "Dataset", "Method" into a single Methods
   section.** JBI body is fixed-shape. Recommend:
   - 1. Introduction (with Statement of Significance box and contributions)
   - 2. Related Work
   - 3. Methods
     - 3.1 Task definition
     - 3.2 Dataset
     - 3.3 Model architecture
     - 3.4 Date normalization
     - 3.5 Baselines
     - 3.6 Experimental setup and metrics
   - 4. Results (move current Section 6 here; keep tables and figures)
   - 5. Discussion (merge current 7 + 8 Limitations)
   - 6. Conclusion (state "the applicability of your research")
   - Followed by required statements (see Section 3 below)
   - References

4. **"Ethics and Privacy" and "Reproducibility" should not be top-level
   numbered sections.** Move them into:
   - Ethics statement: into a dedicated "Ethics" declaration block after the
     Conclusion (the guide treats human-subjects ethics as a *declaration*,
     not a body section). Our synthetic-only design means we state that no
     IRB review was required; this is acceptable but must be in the
     declaration.
   - Reproducibility detail: keep the substantive part inside Methods
     (training hyperparameters, splits, libraries) and move repository
     pointers + raw artifacts pointer into a "Data availability" statement
     and an "Acknowledgements" / Code-availability footnote.

5. **Keywords: keep current count (7) which is within the "1 to 7
   keywords" rule. They go on the title page, not in the abstract section.**
   Current draft puts keywords inside the abstract block — this is
   non-blocking but conventionally they live just below the abstract on the
   title page in Elsevier production.

6. **Title page must list affiliations + a single corresponding author with
   contact.** Our draft has neither author block nor affiliations rendered.
   Add when ready to submit.

7. **Graphical abstract (separate file).** Strongly recommended; "531 x 1328
   pixels (h x w)" minimum. Not strictly required for Original Research, but
   ScienceDirect production will request one. Could be a horizontal pipeline
   diagram derived from `Paper/figures/pipeline.svg`.

8. **Figure / table caption style.** Current draft uses "**Figure N.**"
   bold inline at start of caption — this is fine and matches Elsevier
   production. Tables use `<caption class="note">Table N. ...</caption>` — also
   fine. Make sure every figure and table is cited in the text in numerical
   order (we do this already).

---

## 3. Required Statements We Don't Yet Have

These must appear after the Conclusion and before the References as separate
labelled blocks. Order recommended by Elsevier production:

| Statement | Status | Suggested wording |
|---|---|---|
| **CRediT authorship contribution statement** | MISSING | One sentence per author with comma-separated CRediT roles. Heading: "CRediT authorship contribution statement" (Elsevier-standard). |
| **Declaration of competing interest** | MISSING | If none: "The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper." |
| **Funding** | MISSING | Format: "This work was supported by [agency, grant numbers]" or "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors." |
| **Ethics statement** | PARTIAL (in body Section 9) | Move into declaration block. State: synthetic data, no PHI, no IRB review required. The guide requires for human-subjects work a "statement that all procedures were approved by appropriate institutional committee(s)" with "date and reference number" — not applicable here, but state it explicitly so reviewers don't ask. |
| **Data availability** | PARTIAL (in body Section 10) | Mandatory: "Required to state the availability of any data at submission." Wording: "The synthetic dataset (`synthetic_clinical_notes_2000.csv`), training/inference code, per-system metric files, and figure-generation scripts are available at [repository URL] under [license]." Cite the dataset as a reference if deposited to a permanent repository (Mendeley Data / Zenodo), per JBI Option-C policy: "Required to deposit research data in a relevant data repository." |
| **Generative-AI use disclosure** | MISSING (and we need it) | Required because the synthetic corpus was generated with an LLM. Use Elsevier's mandated wording verbatim, placed "before the references list":
"During the preparation of this work the author(s) used [NAME OF TOOL / SERVICE] in order to [REASON]. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content."
Note: this clause is for AI use *in manuscript preparation*. For AI use as part of the *research method* (i.e., generating the synthetic corpus), the guide separately requires describing it "in a reproducible manner" with "name of the model or tool, version and extension numbers" inside the Methods. We already describe the LLM generator at a high level in Section 4.2; add the model name and version. |
| **Acknowledgements** | MISSING | Optional but conventional. Place after CRediT and before References. |

Image-AI restriction (from the guide): "We do not permit the use of Generative
AI or AI-assisted tools to create or alter images in submitted manuscripts."
Our figures are all matplotlib + an SVG pipeline diagram, so this is fine —
but verify the pipeline.svg was hand-drawn or programmatically generated, not
AI-image-generated.

---

## 4. Reference-Format Conversion Needed

JBI uses Elsevier's **Vancouver-numbered** style. In-text: "Add a number
within square brackets in the text"; references "Number references in the
order they appear".

Our current draft already uses numbered in-text citations like
`<a href="#ref-wang2018">[1]</a>`, which matches the in-text rule. The bibliography is
also numbered. **However, the per-entry formatting needs adjustment** to
match the Elsevier examples:

Current draft entry (example):
```
Wang, Y., Wang, L., ..., and Liu, H. "Clinical information extraction
applications: A literature review." *Journal of Biomedical Informatics*,
77, 34-49, 2018. DOI: 10.1016/j.jbi.2017.11.011.
```

Elsevier-format (from the Guide for Authors):
```
[1] J. van der Geer, T. Handgraaf, R.A. Lupton, The art of writing a
scientific article, J. Sci. Commun. 163 (2020) 51-59.
```

Key differences our draft needs to fix:

- Author format: initials precede surname (`J. van der Geer`), not
  `Surname, F.M.`. All authors written as "F.M. Last", separated by commas.
- Article title: NOT in quotation marks; sentence case is fine.
- Journal name: abbreviated per LTWA ("J. Biomed. Inform." not "Journal of
  Biomedical Informatics"). The guide says: "Abbreviate journal names
  according to the List of Title Word Abbreviations (LTWA)".
- Year: in parentheses immediately after volume.
- Pages: en-dash, no "pp."
- Bracketed reference number `[1]` at start (we have this in the in-text
  cite but not in the bibliography list — easy fix).
- Use `https://doi.org/` URLs for DOIs as "permanent link to the electronic
  article". Our draft has `DOI: 10.xxxx/...` text — convert to live URLs.

Required example formats from the guide (verbatim):

Journal:
> "[1] J. van der Geer, T. Handgraaf, R.A. Lupton, The art of writing a
> scientific article, J. Sci. Commun. 163 (2020) 51-59."

Conference / chapter:
> "[4] G.R. Mettam, L.B. Adams, How to prepare an electronic version of your
> article, in: B.S. Jones, R.Z. Smith (Eds.), Introduction to the Electronic
> Age, E-Publishing Inc., New York, 2020, pp. 281-304."

Dataset:
> "[6] M. Oguro, S. Imahiro, S. Saito, T. Nakashizuka, Mortality data for
> Japanese oak wilt disease... Mendeley Data, v1, 2015."

Conversion plan: rebuild the reference list from `Paper/references.bib` with
a BibTeX style file matching Elsevier numbered references (BibTeX style
`elsarticle-num` from the elsarticle package handles this exactly). If
producing the .docx by hand, render via Pandoc with `--csl elsevier-vancouver.csl`
or use a Zotero/Mendeley plugin set to "Elsevier Vancouver" / "Journal of
Biomedical Informatics" CSL.

---

## 5. Templates and Local Download Paths

JBI does not maintain a JBI-specific Word template. The journal's instructions
are: "Save files in an editable format, using the extension .doc/.docx for
Word files. Format Word files in a single-column layout."

### Templates available

| Template | URL | Local path | Notes |
|---|---|---|---|
| Elsevier generic Word template (CNF) | https://legacyfileshare.elsevier.com/promis_misc/cnf-word-template.docx | `Paper/templates/cnf-word-template.docx` (downloaded, 295 KB) | The "Complete Numbered-References Format" Word template. Single-column, suitable for JBI initial submission. |
| Elsevier elsarticle LaTeX class | https://assets.ctfassets.net/o78em1y1w4i4/4MpsJHO0MOJ2xZuwGTAbOZ/7bc64af36477c5d6cfce335a1f872363/elsarticle.zip | not downloaded | The traditional Elsevier LaTeX class; works for JBI. Use `\documentclass[review,3p,times]{elsarticle}` and `elsarticle-num` bibliography style. |
| Elsevier CAS LaTeX template (single + double column) | https://assets.ctfassets.net/o78em1y1w4i4/5uFmLZJTPDMAUjFnHRpjj8/6f19a979146eb93263763d87a894ab0d/els-cas-templates.zip | not downloaded | Newer "Complex Article Structure" template. Linked directly from JBI Guide for Authors. |
| Overleaf hosted "Elsevier CAS LaTeX Single-Column" | https://www.overleaf.com/latex/templates/elseviers-cas-latex-single-column-template/rsnbvrmnptyq | n/a (online) | If using Overleaf. |

Notes:

- For initial submission, Elsevier accepts "your paper your way" — strict
  template formatting is not enforced before acceptance. So we can submit a
  clean single-column Word or PDF that follows the structural rules without
  pixel-matching the template.
- LaTeX is preferred if we want fewer formatting headaches at typesetting:
  use the elsarticle class with `elsarticle-num` BibTeX style and the
  numbered-bibliography frontmatter macros for structured abstract.

---

## 6. Figure / Table Submission Requirements

From the Guide for Authors:

- Tables: "must be submitted as editable text, not as images"; "avoid vertical
  rules and shading within table cells"; place inline near first citation or
  collected at end. Our HTML uses real `<table>` elements — good; in Word,
  use Word tables (not pasted images) with no vertical rules and minimal
  shading.
- Figures: "Submit each image as a separate file." Cite all in text, "Number
  images according to the sequence they appear" — already satisfied.
- Captions: "brief title (not displayed on the figure itself) and a
  description" — our captions follow this pattern.

File-format and resolution table (verbatim from guide):

| Type | Format | Resolution |
|---|---|---|
| Vector drawings | EPS or PDF | font embedded or text as graphics |
| Color/grayscale photos (halftones) | TIFF, JPG, PNG | min 300 dpi; 1063-2244 px wide |
| Bitmapped line drawings | TIFF, JPG, PNG | min 1000 dpi; 3543-7480 px wide |
| Combinations bitmap + halftone | TIFF, JPG, PNG | min 500 dpi; 1772-3740 px wide |

Our `Paper/figures/` already contains an SVG pipeline diagram and matplotlib
PNGs. For submission: re-export PNGs at 300 dpi minimum, and convert
`pipeline.svg` to PDF or EPS. Verify pixel widths are within the bands above.

Supplementary material policy: "Submit all supplementary materials at the
same time as your manuscript"; "After submission supplementary files can only
be added or replaced in the revision stage"; "These files will not be
checked, formatted or typeset". So our dataset CSV, raw metric JSONs, and
extra figures should be packaged at first submission.

---

## 7. Conventions Confirmed From Recent JBI Papers

Two reference articles inspected:

1. *Optimising clinical information extraction: a comparative study of
   retrieval-augmented generation techniques in clinical notes* (Zhang et
   al., 2026). DOI 10.1016/j.jbi.2026.105053. Article in press — confirms
   structured abstract and pre-references declaration block ordering.
2. *Contextualized Medication Information Extraction Using Transformer-based
   Deep Learning Architectures* (Chen et al.). PMC10980542 — confirmed JBI
   article. Section headings in all-caps, unnumbered (Introduction /
   Background / Methods / Results / Discussion and Conclusion /
   Acknowledgments). Abstract: Objective / Materials and Methods / Results /
   Conclusion. Numbered in-text citations `[#]`. Author roles given in a
   "Contributorship statement", competing interests explicitly stated,
   funding statement lists NIH grant numbers, data availability points to
   the n2c2 challenge website plus a GitHub repo.

Inferences:

- Numbered section headings (`1. Introduction`, etc.) are common but not
  required; ALL-CAPS unnumbered headings are also acceptable. We can keep
  numbered headings (cleaner cross-referencing).
- Abstract structured headings are flexible: "Materials and Methods" is
  accepted in place of "Methods", but the four-block Objective / Methods /
  Results / Conclusion structure is invariant.
- "Conclusion(s) must state the applicability of your research" — emphasize
  this in the rewrite.
- Generative-AI corpus generation should be described in Methods with
  explicit model name + version (e.g., `gpt-4o-2024-08-06`).

---

## 8. Pre-Submission Checklist

### Manuscript content

- [ ] Rename abstract sub-headings to Objective / Methods / Results /
      Conclusion; cap at 300 words.
- [ ] Add 150-word "Statement of Significance" table at end of Introduction
      with the four mandated sub-headings.
- [ ] Merge sections 3-6 into a single numbered Methods section with
      sub-sections; promote 6.3 Results into a top-level Results section.
- [ ] Move Ethics into a declaration block; move Reproducibility detail into
      Methods + Data availability.
- [ ] Verify body word count <=6000 (excluding abstract, references,
      statements, captions).
- [ ] Verify figure + table count <=8 (currently 6 + 2 = 8; at the cap).
- [ ] Add Conclusion sentence stating clinical applicability.

### Front matter

- [ ] Title page: full author list, affiliations, corresponding author with
      email and ORCID.
- [ ] 1-7 keywords (current 7 OK).
- [ ] Optional graphical abstract at minimum 531 x 1328 px (h x w).

### Required statements (after Conclusion, before References)

- [ ] CRediT authorship contribution statement (heading: "CRediT
      authorship contribution statement")
- [ ] Declaration of competing interest
- [ ] Funding
- [ ] Ethics statement (state "no IRB review required, synthetic data, no
      PHI" explicitly)
- [ ] Data and code availability (with persistent repository URL or DOI,
      e.g., Zenodo deposit; cite the dataset as a reference too)
- [ ] Generative-AI use disclosure (verbatim Elsevier wording, with tool
      names and versions)
- [ ] Acknowledgements (optional)

### Methods-side AI disclosure

- [ ] In Methods (Dataset section), name the LLM used to generate the
      corpus, version, key parameters (temperature, prompts archived), per
      Elsevier's "reproducible manner" rule.

### References

- [ ] Convert bibliography to Elsevier numbered style (`elsarticle-num` /
      "Elsevier Vancouver" CSL): authors as "F.M. Last", journal abbreviated
      per LTWA, year in parentheses after volume, en-dash page ranges, no
      quote marks around titles, `[N]` prefix on each entry.
- [ ] Replace "DOI: 10.xxx" text with full `https://doi.org/10.xxx` URLs.
- [ ] Verify that every reference is cited in the body and numbered in
      order of first appearance.

### Figures and tables

- [ ] Re-export bitmap figures at >=300 dpi (1063-2244 px wide for
      color/halftone).
- [ ] Convert `pipeline.svg` to vector PDF or EPS with embedded fonts.
- [ ] Save each figure as a separate file (Figure_1.pdf, Figure_2.png, ...).
- [ ] Tables in editable Word table form; no vertical rules, minimal shading.

### Supplementary material (one zip at submission)

- [ ] `synthetic_clinical_notes_2000.csv`
- [ ] Per-system raw predictions (when available)
- [ ] Strict-JSON metric files
- [ ] Annotation guidelines / data card
- [ ] Optional: model card, example prompts for ChatGPT and LLaMA baselines

### Submission mechanics

- [ ] Editorial Manager at https://www.editorialmanager.com/jbi/default.aspx
- [ ] Article type: Research Paper
- [ ] Cover letter highlighting hybrid neural-symbolic design, the
      action-date reliability gain, and the explicit synthetic-only scope.
- [ ] Confirm preprint policy if posting to SSRN/arXiv (allowed; "no effect
      on the editorial process").
- [ ] Single peer-review process; expect at least 2 reviewers.

---

## 9. Useful Direct Quotes (for in-paper or cover-letter use)

- Body structure: "Introduction, Related Work, Methods, Results, Discussion,
  and Conclusion; with a total of <=6000 words"
- Abstract: "Structured abstract (Objective, Methods, Results, Conclusion;
  with a total of <=300 words)"
- Figures + tables cap: "total number of figures and tables <=8"
- Statement of Significance: "summaries (in 150 words or less)" with
  sub-headings "Problem or Issue", "What is Already Known", "What this Paper
  Adds", "Who would benefit from the new knowledge in this paper"; "should
  also be part of the Introduction section of the paper"
- AI use in writing: "During the preparation of this work the author(s) used
  [NAME OF TOOL / SERVICE] in order to [REASON]. After using this tool/
  service, the author(s) reviewed and edited the content as needed and
  take(s) full responsibility for the content."
- AI in images: "We do not permit the use of Generative AI or AI-assisted
  tools to create or alter images in submitted manuscripts."
- AI as method: must describe in "reproducible manner" with "name of the
  model or tool, version and extension numbers"
- Data: "Required to state the availability of any data at submission";
  Option-C: "Required to deposit research data in a relevant data
  repository"
- References: "Add a number within square brackets in the text"; "Number
  references in the order they appear"; "Abbreviate journal names according
  to the List of Title Word Abbreviations (LTWA)"
- Tables: "must be submitted as editable text, not as images"; "Avoid
  vertical rules and shading within table cells"
- Word format: "Format Word files in a single-column layout"
