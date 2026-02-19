# spk-content-anon – Evaluation Scripts

Evaluation suite for **speaker** and **content** anonymization. Contains:

- **ASV** (automatic speaker verification): privacy via EER/FAR
- **ASR** (automatic speech recognition): utility via WER
- **MOS** (mean opinion score): quality via VoiceMOS

---

## 1. ASV Evaluation (`eval/asv/`)

**Purpose**: Measure how well speaker identity is hidden (privacy).

**Main script**: `compute_em.py`  
Uses ECAPA-VoxCeleb to compute speaker embeddings and:

1. Builds **positive pairs** (same speaker) and **negative pairs** (different speakers) from a TSV
2. Computes cosine similarity scores for:
   - `pos`: original vs original (same speaker)
   - `neg`: original vs original (different speakers)
   - `oa`: original vs anonymized (same utterance anonymized)
3. Fits EER on pos/neg, then measures FAR on `oa` (lower = more privacy)

**Inputs**:

| Arg | Description |
|-----|-------------|
| TSV file | `id` and `speaker_id` columns (tab-separated) |
| `ori_dir` | Original audio directory (`*.ogg` or `*.wav`) |
| `anon_dir` | Anonymized audio directory (`*.wav`) |
| `out` | Output directory for `.npy` scores and plot |

**Example**:
```bash
python compute_em.py sample/sample.tsv sample/ori sample/anon exp
```

---

## 2. ASR Evaluation (`eval/asr/`)

**Purpose**: Measure how well speech content is preserved (utility).

**Model**: wav2vec2 (`facebook/wav2vec2-large-960h-lv60-self`, English 16kHz)

**Scripts**:
- `predict.py`: Transcribe audio with wav2vec2
- `compute_wer.py`: Compute WER from reference vs hypothesis

**Inputs**:
- `datadir`: Directory with `.wav` (or `.flac`, `.mp3`, `.ogg`)
- `ref.txt`: Reference transcriptions (`utt_id ref_text`)

**Example**:
```bash
bash eval/asr/run.sh                    # uses sample/datadir, sample/ref.txt
bash eval/asr/run.sh my_wavs/ my_ref.txt
```

---

## 3. MOS Evaluation (`eval/mos/`)

**Purpose**: Measure perceived quality (VoiceMOS).

Uses finetuned SSL model for MOS prediction. Requires:
- Fairseq base model (wav2vec2)
- Finetuned checkpoint
- Resampled 16kHz normalized wavs and `sets/val_mos_list.txt`

**Running MOS separately** (needs classic `fairseq`; PyTorch 2.6+ needs `weights_only=False` patch in predict.py):

```bash
# 1. Create MOS input
cd /app/multispk-anon/spk-content-anon
mkdir -p exp_sample/mos_sample/wav exp_sample/mos_sample/sets
cp sample/anon/*.wav exp_sample/mos_sample/wav/
ls exp_sample/mos_sample/wav/*.wav | xargs -I{} basename {} | sed 's/$/,1.0/' > exp_sample/mos_sample/sets/val_mos_list.txt

# 2. Run VoiceMOS inference (downloads fairseq + checkpoint if needed)
cd eval/mos/mos-finetune-ssl
python run_inference_for_challenge.py --datadir $(pwd)/../../exp_sample/mos_sample

# 3. Copy to exp_sample and get mean
cp answer_main.txt ../../exp_sample/mos_answer.txt
awk '{ total += $2; count++ } END { print total/count }' ../../exp_sample/mos_answer.txt
```

---

## Sample Data & Quick Run

**1. Prepare sample data** (from libri_dev_enrolls; uses `text` for ref.txt):
```bash
cd /app/multispk-anon/spk-content-anon
bash scripts/prepare_sample.sh
# Optional: use custom Kaldi data dir (wav.scp, text, utt2spk):
#   bash scripts/prepare_sample.sh /path/to/data/libri_dev_enroll
```

**2. Run evaluation** (ASV + ASR + MOS if fairseq installed):
```bash
bash scripts/run_sample.sh              # full run
bash scripts/run_sample.sh --dry-run    # show commands, check inputs, no execution
```

Output: `exp_sample/` – FAR report, DET plot (ASV), hyp.txt (ASR), WER.

**Sample layout:**
- `sample/ori/` – original wavs (5 files)
- `sample/anon/` – anonymized wavs (same as ori for demo; replace with real anonymized audio)
- `sample/datadir/` – for ASR predict.py
- `sample/sample.tsv` – id, speaker_id
- `sample/ref.txt` – reference transcripts for WER
