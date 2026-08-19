# JBI R1 Reviewer Comments

**Journal:** Journal of Biomedical Informatics (JBI)
**Manuscript:** *Reliable Extraction of Clinical Follow-Up Instructions: A Hybrid Neural-Symbolic Pipeline*
**Corresponding author:** Dr Yehudit Aperstein (Afeka College of Engineering)
**Acting Editor-in-Chief:** Dr Guy Tsafnat
**Editorial system:** Editorial Manager — "Submissions with a Decision" folder
**Received:** 2026-08-19
**Round:** 1 (post-initial-submission)

---

## Editor's cover message

> Dear Dr Aperstein,
>
> Experts in the field have now reviewed your paper, referenced above.
>
> To view your reviewer feedback, please log in as an author at https://www.editorialmanager.com/jbi/ and navigate to your manuscript in the "Submissions with a Decision" folder under the Author Main Menu.
>
> We have attached the reviewers' comments below to help you to understand the basis for our decision. We hope that their thoughtful comments will help you in future submissions to the JBI and in your future studies.
>
> Sincerely,
> Dr. Guy Tsafnat
> Acting Editor-in-Chief
> Journal of Biomedical Informatics

---

## Editor's summary of reviewer consensus

> The reviewers agree that the paper is well written and relevant, and the described method is potentially important to the field. However, they also both agree that the current evaluation lacks rigor due to its reliance on synthetic data.

---

## Reviewer 1

The paper explores a clinical information extraction task focused on identifying follow-up recommendations specifically by identifying TestSpecification (action) and TimeSpecification (time) entities that are linked through a ScheduleFor relation. The TestSpecification entity includes a fixed set of labels from a closed ontology. The TimeSpecification is normalized to a day offset. The action spans are normalized using a dictionary, and the type spans are normalized using a rule grammar. *[Editor's note: "type spans" appears to be a transcription artifact for "time spans".]*

The evaluation is performed exclusively with a new synthetic corpus of outpatient notes.

The manuscript indicates that this synthetic corpus is intended to avoid PHI constraints and define a clear ground truth for entities, relations, and normalized timing. The corpus covers five domains. TestSpecification labels are based on 28 canonical action types, and TimeSpecification our day offsets. TimeSpecification is rendered using multiple phrase families. The corpus is intended to capture variations in clinician voice, hairstyle, structural formatting, abbreviations, dictation-like artifacts, etc. Notes were generated using GPT 4o-mini. *["hairstyle" and "our day offsets" appear to be transcription artifacts for "plan-header style" and "as day offsets".]*

The manuscript compares a BERT-based architecture with GPT 4o-mini in zero-shot and Llama 3 8B fine-tuned. The BERT-based model achieves near perfect performance for the end-to-end evaluation that requires identifying and normalizing both the action and time and linking through a relation (0.986 and 0.997 F1). **This near-perfect performance is a red flag that undermines the results.** The BERT model is likely learning GPT-4o-mini's expression of the defined phenomena, even with the attempts to make the synthetic notes realistic. Temporal and relation clinical extraction tasks are notoriously challenging, even for human annotators (as judged by IAA that are much lower than the achieved extraction performance year). *["year" appears to be a transcription artifact for "here".]*

BERT models are generally "easier" to fit to discriminative tasks as they are discriminative models. However, it is not clear why the fine-tuned Llama performance is not at least closer to the BERT model's performance. I would not expect Llama to necessarily beat BERT, but my intuition is that a fine-tuned Llama model would have reasonable performance.

The manuscript contributions include the synthetic corpus and the comparative analysis between the fine-tuned BERT architecture and the two LLMs variants. It does not present a new information extraction approach. Given the near-perfect performance of the BERT-based information extraction model, the corpus lacks the heterogeneity of real-world corpora, which undermines this contribution. The utility of the comparative analysis relies on the goodness of this corpus, where goodness is about realism and the proxy for real-data. The limited comparison with MTSamples does not demonstrate this realism. Additionally, information extraction performance on real-world data is likely needed to understand the relationship between the synthetic corpus performance and real-world performance.

### Reviewer 1 — Detailed feedback

**§2 Related Work.** The related work section does a good job of identifying how the presented work fits within the larger body of research, including identifying how it is differentiated. The related work has a description of synthetic clinical data, where it explicitly indicates that the presented corpus should be viewed as a controlled evaluation, not evidence the model is ready for clinical deployment.

**§3 Methods.** The language of the synthetic corpus should be explicitly stated.

**§3.3 Hybrid neuro-symbolic architecture.** The presented architecture is very similar to several preceding publications. Although some of these are certainly acknowledged in Related Work, where the architecture clearly is drawn from existing work, the relevant paper should be cited. As an example, the span representation is very similar to existing BERT-based work.

The normalization of TestSpecification and TimeSpecification spans is both deterministic. For test/action, this appears to be achieved through a dictionary map. For time, this is described as a rule grammar over phrase families.

The actions were partitioned into 18 training types, 4 validation types, and 6 test types. The intent here is to have a validation and test actions that are not present in the train corpus. The evaluation includes two test set partitions, one with actions that are in the training set and one with actions that are not in the training set ("scene-test" versus "OOV-test"). *["scene-test" appears to be a transcription artifact for "seen-test".]*

**§3.5 Evaluation metrics.** Four different evaluation criteria are presented. These seem like appropriate measures.

---

## Reviewer 3

### Overall

This manuscript addresses an important clinical NLP task, extracting follow up actions, linking them to temporal expressions, and normalizing dates. The modular design is interpretable, and the controlled benchmark is potentially useful. However, the evidence does not fully support the broader claims about LLM limitations or clinical applicability. The evaluation is almost entirely synthetic, the LLM comparison appears insufficiently optimized, and the methodological novelty is limited.

### Major comments

**1. The LLM comparison is not sufficiently convincing or fair.**
The manuscript repeatedly claims that recent LLMs recognize actions well but commonly fail at linking and date arithmetic. This conclusion rests only on GPT4o mini and LLaMA 3 8B under one specific prompting and fine tuning configuration, with no in-context examples, no tool use, and no constrained decoding (as mentioned in the manuscript). These are relatively small and minimally optimized baselines, and the very large performance gap raises concern that the prompts, output schema, or post processing may not be fully optimized for the baselines. The statement that linking and arithmetic fail because they are "implicit in generation" is a reasonable hypothesis but is not directly established by the current experiments, since no ablation isolates linking failures from arithmetic failures within the generative baselines.

**2. Synthetic evaluation limits the main conclusions.**
The MTSamples analysis is a limited realism check rather than external validation. MTSamples may also differ substantially from operational EHR notes in structure and style. No end-to-end system performance is reported on any independent real-text dataset. Given this, claims regarding scheduling auditors, clinical reliability, and generalizability should be stated more cautiously. The authors do acknowledge this limitation in the manuscript, but it still substantially constrains the strength of the conclusions drawn elsewhere in the paper.

**3. The methodological novelty appears incremental.**
Combining a BioBERT encoder, biaffine relation linking, ontology mapping, and rule based temporal normalization is a reasonable engineering choice but not clearly novel on its own, as the authors themselves note that the contribution lies in the task decomposition rather than the individual components. The authors should more clearly distinguish their contribution from prior work on clinical recommendation extraction, event time linking, joint entity relation extraction, and temporal normalization. Stronger conventional baselines (for example a rule only pipeline, or an ablation isolating the encoder choice) and additional ablation studies would help demonstrate that the contribution extends beyond task specific integration of existing components.

**4. The task excludes clinically important follow-up types.**
As the authors note in future work, conditional follow-up instructions (for example "return if symptoms worsen") are clinically common but are not supported by the current ontology. The realism check itself shows that roughly 60 percent of real follow up items fall outside the closed set ontology, including medication titration and conditional or self-care instructions. Since this directly affects claims of clinical applicability, this limitation should be discussed more prominently in the main text rather than only in the Limitations and future work section, with a clearer account of how the ontology would need to be extended.

**5. Error analysis needs quantitative support.**
In Table 3, labels such as "high," "moderate," "low," and "rare" are not interpretable without counts or denominators. Please report the number and percentage of each error type, ideally broken down by model and by test split, so the qualitative error profile can be verified and compared across systems.

### Minor comments

1. Figure 2 appears to contain overlapping graphical elements and should be reformatted for clarity.
2. Please avoid terms such as "trustworthy" or "reliable" in the abstract and conclusion unless they are supported by real-world external validation or substantially stronger experimental evidence.

---

## Boilerplate footer from the editorial email

```
FAQ: How can I reset a forgotten password?
https://service.elsevier.com/app/answers/detail/a_id/28452/supporthub/publishing/kw/editorial+manager/

For further assistance, please visit our customer service site:
https://service.elsevier.com/app/home/supporthub/publishing/.
Here you can search for solutions on a range of topics, find answers to
frequently asked questions, and learn more about Editorial Manager via
interactive tutorials. You can also talk 24/7 to our customer support team
by phone and 24/7 by live chat and email.

At Elsevier, we want to help all our authors to stay safe when publishing.
Please be aware of fraudulent messages requesting money in return for the
publication of your paper. If you are publishing open access with Elsevier,
bear in mind that we will never request payment before the paper has been
accepted. We have prepared some guidelines that you may find helpful,
including a short video on Identifying fake acceptance letters. Please
remember that you can contact Elsevier's Researcher Support team at any
time if you have questions about your manuscript, and you can log into
Editorial Manager to check the status of your manuscript.

#AU_JBI#
```
