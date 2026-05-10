# External Model Artifacts

This document inventories every model artifact referenced by the
notebook (`Code/llm_project_follow_up_instruction_extraction_2k_dataset_submit.ipynb`)
that lives outside this repository, where it currently sits, and how to
populate `models/` so the eval pipeline can be re-run end-to-end.

## A. Fine-tuned task checkpoints (private Google Drive)

These were trained by the original course run and saved to the user's
personal Google Drive. **They are not publicly mirrored** and are not
downloadable without the user's Drive credentials. The notebook's
hard-coded paths are:

| Drive path | Purpose | Approx. size | Local target |
|---|---|---|---|
| `MyDrive/BioBERT-Finetuned-Model.bin` | BioBERT joint NER + linking head, full state_dict | ~440 MB | `models/biobert-finetuned/pytorch_model.bin` |
| `MyDrive/biobert_finetuned_2k.pth` | Same head, alternate save (used for the 2k-dataset run reported in the paper) | ~440 MB | `models/biobert-finetuned/biobert_finetuned_2k.pth` |
| `MyDrive/biobert_finetuned.pth` | Earlier checkpoint, kept for provenance | ~440 MB | `models/biobert-finetuned/biobert_finetuned.pth` (optional) |
| `MyDrive/BioBERT-Finetuned-Tokenizer/` | HuggingFace tokenizer directory (vocab.txt, tokenizer_config.json, special_tokens_map.json) | ~few MB | `models/biobert-finetuned-tokenizer/` |
| `MyDrive/Llama3_Clinical_Action_Extraction_LoRA/` | LoRA adapter directory for Meta-Llama-3-8B (adapter_model.safetensors + adapter_config.json + tokenizer files) | ~150 MB | `models/llama3-clinical-action-extraction-lora/` |
| `MyDrive/llama-3-finetuned-results/` | Older LLaMA results dir (training logs, possibly an older adapter) | ~150 MB | `models/llama3-finetuned-results/` (optional) |
| `MyDrive/biobert_finetuned_metrics.json` | Already mirrored at `Results/biobert_metrics.json` | ~1 KB | already present |
| `MyDrive/llama_finetuned_metrics.json` | Already mirrored at `Results/llama_metrics.json` | ~1 KB | already present |

### How to bring them down

Pick one option:

**Option 1 — gdown with shared link (fastest, public).**
For each Drive file, right-click in Drive UI → "Share" → "Anyone with the link" → copy URL → extract the file ID, then:

```bash
# Single file (e.g. biobert_finetuned_2k.pth):
/c/Python314/python -m gdown "https://drive.google.com/uc?id=<FILE_ID>" -O models/biobert-finetuned/biobert_finetuned_2k.pth

# Folder (e.g. tokenizer dir or LoRA adapter):
/c/Python314/python -m gdown --folder "https://drive.google.com/drive/folders/<FOLDER_ID>" -O models/biobert-finetuned-tokenizer
```

`gdown` is already installed (`/c/Users/apart/AppData/Roaming/Python/Python314/Scripts/gdown`).

**Option 2 — rclone with personal Drive auth (no sharing required).**
Install rclone, run `rclone config` and add a Google Drive remote, then:

```bash
rclone copy gdrive:BioBERT-Finetuned-Model.bin     models/biobert-finetuned/
rclone copy gdrive:biobert_finetuned_2k.pth        models/biobert-finetuned/
rclone copy gdrive:BioBERT-Finetuned-Tokenizer     models/biobert-finetuned-tokenizer/ -P
rclone copy gdrive:Llama3_Clinical_Action_Extraction_LoRA models/llama3-clinical-action-extraction-lora/ -P
```

**Option 3 — manual copy.**
Open Drive in a browser, download the four artifacts as zip, extract into the `models/` subdirectories shown above.

### After download

Verify the files match the notebook's expected names. For the BioBERT
state_dict, the eval cell expects to load via `torch.load()` and
populate a `BioBertNerLinker` instance defined in cell 18 of the
notebook. The LLaMA LoRA adapter is loaded by `unsloth.FastLanguageModel.from_pretrained()`.

## B. Public base-model dependencies (HuggingFace Hub)

These are the upstream pretrained models that are *not* downloaded into
this repo (each is large and HuggingFace caches them centrally on first
`from_pretrained()` call):

| HuggingFace ID | Role | Size | Access |
|---|---|---|---|
| `dmis-lab/biobert-base-cased-v1.1` | Base encoder for the hybrid pipeline | ~440 MB | Public |
| `meta-llama/Meta-Llama-3-8B` | Base model fine-tuned for the LLaMA baseline | ~16 GB | **Gated** — requires Meta license acceptance + HF token |
| `unsloth/llama-3-8b-instruct-bnb-4bit` | 4-bit quantized LLaMA used by `unsloth.FastLanguageModel` for inference | ~5 GB | **Gated** (same Meta license) |

These will be downloaded on demand into `~/.cache/huggingface/hub/` the
first time the inference code runs. There is no need to commit them to
this repo. To pre-cache the BioBERT base:

```bash
/c/Python314/python -c "from transformers import AutoModel, AutoTokenizer; AutoTokenizer.from_pretrained('dmis-lab/biobert-base-cased-v1.1'); AutoModel.from_pretrained('dmis-lab/biobert-base-cased-v1.1')"
```

For the LLaMA bases, set `HF_TOKEN` first (`export HF_TOKEN=hf_...` after
accepting the Meta license at https://huggingface.co/meta-llama/Meta-Llama-3-8B).

## C. External services (no checkpoint, but required for re-running)

| Service | Used for | Auth required |
|---|---|---|
| OpenAI API (`gpt-4o-mini`) | ChatGPT zero-shot baseline (cells 49 / 63) | `OPENAI_API_KEY` env var, billing enabled |

A full re-run of the held-out evaluation costs roughly $0.10-$0.50 in
OpenAI credits at current `gpt-4o-mini` pricing (198 notes, ~1500 tokens
prompt + ~150 tokens response each).

## D. Other external references in the repo

| File / reference | Status |
|---|---|
| `README.md` line 8: `<img src="visual_abstract/visual_abstract.png">` | **Broken** — no such file in the repo. The file `visual_abstract.png` does not exist; closest existing visuals are in `Visuals/` and `Paper/figures/`. Fix by either pointing at an existing visual or adding the missing image. |
| `Code/.gitkeep`, `Data/.gitkeep`, etc. | Placeholder files only; nothing missing. |
| `Slides/*.pptx`, `Slides/*.pdf` | Self-contained in repo. |

## Reproducing per-note predictions

The eval functions (notebook cells 26 BioBERT, 53 LLaMA, 63 ChatGPT)
compute per-note results in memory but only persist aggregate metrics.
To recover full per-note predictions:

1. Download the artifacts in section A above so the trained models are
   available locally.
2. Patch the eval cells to dump per-note records:
   ```python
   per_note_records.append({
       "note_id": idx, "gold": gt_pairs, "pred": s_pred_pairs,
       "gold_dates": gt_map, "pred_dates": s_pred_map,
       "abs_err_days": [...]})
   ```
   then `pd.DataFrame(per_note_records).to_json("predictions/llama.jsonl", orient="records", lines=True)`.
3. Re-run cells 26 / 53 / 63 against `df_test_clean` (198 notes).
4. Bootstrap confidence intervals can then be computed at the note
   level rather than the reconstructed-instance level used in
   `Paper/scripts/compute_confidence_intervals.py`.

This is *not* a new experiment (same models, same data, same metrics);
it just persists data the existing eval already computes.
