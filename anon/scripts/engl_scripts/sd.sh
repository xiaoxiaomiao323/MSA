#!/bin/bash

# ==============================================================================
# Copyright (c) 2024, Singapore Institute of Technology
# Author: Xiaoxiao Miao (xiaoxiao.miao@singaporetech.edu.sg)
# All rights reserved.
# ==============================================================================


source env.sh

datadir=anon/data/$1



type=res
xv_dir=none
echo generate resynthesis conversation
python anon/adapted_from_facebookresearch/inference.py --input_test_file $datadir/wav_mix.scp \
        --input_test_rttm $datadir/rttms \
                --checkpoint_file anon/pretrained_models_anon_xv/HiFi-GAN/libri_tts_clean_100_fbank_xv_ssl_freeze \
                --output_dir exp/output_speech/predict_rttm/$1_${type} \
                --xv_dir $xv_dir


type=select
echo generate anonymized conversation using selection-base anonymizer
xv_dir=anon/selec_anon/output_anon_spk_vector/$1/pseudo_xvectors/xvectors/
python anon/adapted_from_facebookresearch/inference.py --input_test_file $datadir/wav_mix.scp \
        --input_test_rttm $datadir/rttms \
                --checkpoint_file anon/pretrained_models_anon_xv/HiFi-GAN/libri_tts_clean_100_fbank_xv_ssl_freeze \
                --output_dir exp/output_speech/predict_rttm/$1_${type} \
                --xv_dir $xv_dir

for type in ds as; do
echo generate anonymized conversation using $type-base anonymizer
xv_dir=anon/anon_control/exp/$type/$1
python anon/adapted_from_facebookresearch/inference.py --input_test_file $datadir/wav_mix.scp \
        --input_test_rttm $datadir/rttms \
		--checkpoint_file anon/pretrained_models_anon_xv/HiFi-GAN/libri_tts_clean_100_fbank_xv_ssl_freeze \
		--output_dir exp/output_speech/predict_rttm/$1_${type} \
		--xv_dir $xv_dir
done
