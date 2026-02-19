#!/usr/bin/env python3
"""Transcribe audio with wav2vec2 for WER evaluation."""
import argparse
import glob
import os
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("datadir", help="Directory with .wav (or .flac, .mp3, .ogg)")
    parser.add_argument("output", help="Output text file (utt_id hypothesis)")
    parser.add_argument("--model", default="facebook/wav2vec2-large-960h-lv60-self")
    args = parser.parse_args()

    processor = Wav2Vec2Processor.from_pretrained(args.model)
    model = Wav2Vec2ForCTC.from_pretrained(args.model)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    exts = ("*.wav", "*.flac", "*.mp3", "*.ogg")
    wavs = []
    for ext in exts:
        wavs.extend(glob.glob(os.path.join(args.datadir, ext)))
    wavs = sorted(set(wavs))

    with open(args.output, "w") as f:
        for wav in wavs:
            audio, sr = torchaudio.load(wav)
            if sr != 16000:
                audio = torchaudio.functional.resample(audio, sr, 16000)
            input_values = processor(audio.squeeze().numpy(), sampling_rate=16000, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = model(input_values.input_values.to(device)).logits
            ids = torch.argmax(logits, dim=-1)[0]
            hyp = processor.decode(ids)
            utt_id = os.path.splitext(os.path.basename(wav))[0]
            f.write(f"{utt_id} {hyp}\n")

    print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()
