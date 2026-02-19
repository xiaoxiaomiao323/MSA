# Evaluation Scripts

ASV (privacy/FAR), ASR (utility/WER), MOS (quality). Sample provided.

```bash
bash scripts/run_sample.sh
```

Output: `exp_sample/` – WER, FAR, MOS.

---

**ASV** (`eval/asv/`): TSV + ori_dir + anon_dir → FAR  

**ASR** (`eval/asr/`): wav dir + ref.txt → WER  

**MOS** (`eval/mos/`): VoiceMOS on 16 kHz wavs → mean score  
