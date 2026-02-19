#!/bin/bash
# Run ASV (FAR), ASR (WER), and MOS evaluation on sample data
# Prerequisites: pip install torch torchaudio speechbrain scikit-learn pandas matplotlib transformers
# MOS: pip install fairseq scipy (optional, for VoiceMOS)
# Usage: ./run_sample.sh [--dry-run]

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
SAMPLE="$ROOT/sample"
EXP="$ROOT/exp_sample"
MOS_DIR="$ROOT/eval/mos/mos-finetune-ssl"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

cd "$ROOT"

# Ensure sample data exists
if [[ ! -f "$SAMPLE/sample.tsv" ]]; then
  if $DRY_RUN; then
    echo "[DRY RUN] Would run: bash $SCRIPT_DIR/prepare_sample.sh"
  else
    echo "Preparing sample data..."
    bash "$SCRIPT_DIR/prepare_sample.sh"
  fi
fi

if $DRY_RUN; then
  echo ""
  echo "========== DRY RUN =========="
  echo "Would create: $EXP/"
  echo ""
  echo "1. ASV (FAR):"
  echo "   python eval/asv/compute_em.py $SAMPLE/sample.tsv $SAMPLE/ori $SAMPLE/anon $EXP"
  echo ""
  echo "2. ASR (WER):"
  echo "   python eval/asr/predict.py $SAMPLE/datadir $EXP/hyp_wav2vec2.txt --model facebook/wav2vec2-large-960h-lv60-self"
  echo "   python eval/asr/compute_wer.py --mode present $SAMPLE/ref.txt $EXP/hyp_wav2vec2.txt"
  echo ""
  echo "3. MOS (if fairseq installed):"
  echo "   Prepare $EXP/mos_sample/, run eval/mos/mos-finetune-ssl/predict.py"
  echo ""
  echo "Inputs check:"
  for f in "$SAMPLE/sample.tsv" "$SAMPLE/ref.txt"; do [[ -f "$f" ]] && echo "  OK $f" || echo "  MISSING $f"; done
  for d in "$SAMPLE/ori" "$SAMPLE/anon" "$SAMPLE/datadir"; do [[ -d "$d" ]] && echo "  OK $d ($(ls -1 "$d" 2>/dev/null | wc -l) wavs)" || echo "  MISSING $d"; done
  echo "============================="
  exit 0
fi

mkdir -p "$EXP"

# --- ASV (FAR) ---
echo "=== ASV Evaluation (FAR) ==="
python eval/asv/compute_em.py \
  "$SAMPLE/sample.tsv" \
  "$SAMPLE/ori" \
  "$SAMPLE/anon" \
  "$EXP" 2>&1 | tee "$EXP/asv_log.txt"
FAR=$(grep -oP 'False acceptance rate: \K[\d.]+' "$EXP/asv_log.txt" 2>/dev/null || echo "")
echo "ASV output: $EXP/*.npy, $EXP/*.png"
echo ""

# --- ASR (WER) ---
echo "=== ASR Transcription (wav2vec2) ==="
python eval/asr/predict.py "$SAMPLE/datadir" "$EXP/hyp_wav2vec2.txt" \
  --model facebook/wav2vec2-large-960h-lv60-self 2>&1
echo ""

echo "=== WER Computation ==="
python eval/asr/compute_wer.py --mode present "$SAMPLE/ref.txt" "$EXP/hyp_wav2vec2.txt" 2>&1 | tee "$EXP/wer_log.txt"
WER=$(grep -oP '%WER \K[\d.]+' "$EXP/wer_log.txt" 2>/dev/null || echo "")
echo ""

# --- MOS (optional) ---
MOS_MEAN=""
if python -c "import fairseq" 2>/dev/null; then
  echo "=== MOS Evaluation (VoiceMOS) ==="
  MOS_DATADIR="$EXP/mos_sample"
  mkdir -p "$MOS_DATADIR/wav" "$MOS_DATADIR/sets"
  cp "$SAMPLE/anon"/*.wav "$MOS_DATADIR/wav/" 2>/dev/null || cp "$SAMPLE/datadir"/*.wav "$MOS_DATADIR/wav/" 2>/dev/null
  ls "$MOS_DATADIR/wav"/*.wav 2>/dev/null | xargs -I{} basename {} | sed 's/$/,1.0/' > "$MOS_DATADIR/sets/val_mos_list.txt"
  if [[ -s "$MOS_DATADIR/sets/val_mos_list.txt" ]]; then
    cd "$MOS_DIR"
    if [[ ! -f fairseq/wav2vec_small.pt ]]; then
      echo "MOS: downloading wav2vec_small.pt from Facebook..."
      mkdir -p fairseq
      wget -q https://dl.fbaipublicfiles.com/fairseq/wav2vec/wav2vec_small.pt -P fairseq/ || true
    fi
    if [[ ! -f pretrained/ckpt_w2vsmall ]]; then
      echo "MOS: downloading ckpt_w2vsmall..."
      mkdir -p pretrained
      wget -q -L "https://github.com/xiaoxiaomiao323/MSA/releases/download/new-main/ckpt_w2vsmall" -O pretrained/ckpt_w2vsmall 2>/dev/null || true
    fi
    if [[ -f fairseq/wav2vec_small.pt ]] && [[ -f pretrained/ckpt_w2vsmall ]]; then
      if python predict.py --fairseq_base_model fairseq/wav2vec_small.pt \
        --finetuned_checkpoint pretrained/ckpt_w2vsmall \
        --datadir "$MOS_DATADIR" \
        --outfile "$EXP/mos_answer.txt" 2>&1; then
        MOS_MEAN=$(awk '{ total += $2; count++ } END { if(count>0) printf "%.2f", total/count }' "$EXP/mos_answer.txt" 2>/dev/null)
      else
        echo "MOS predict.py failed (fairseq API mismatch? Use: conda env create -f eval/mos/mos-finetune-ssl/environment.yml)"
      fi
    else
      echo "MOS: run 'cd eval/mos/mos-finetune-ssl && python run_inference_for_challenge.py --datadir $MOS_DATADIR' to download models first"
    fi
    cd "$ROOT"
  fi
  echo "MOS output: $EXP/mos_answer.txt"
else
  echo "=== MOS Evaluation (skipped: pip install fairseq scipy) ==="
fi
echo ""

# --- Summary ---
echo "========== SUMMARY =========="
echo "WER:  ${WER:-N/A}%"
echo "FAR:  ${FAR:-N/A}%"
echo "MOS:  ${MOS_MEAN:-N/A} (mean predicted score)"
echo "============================="
echo "Done. Results in $EXP/"
