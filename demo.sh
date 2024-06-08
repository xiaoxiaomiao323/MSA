#!/bin/bash
# ==============================================================================
# Copyright (c) 2024, Singapore Institute of Technology
# Author: Xiaoxiao Miao (xiaoxiao.miao@singaporetech.edu.sg)
# All rights reserved.
# ==============================================================================


source env.sh

stage=1
stop_stage=7
rootdir=$PWD
if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    echo "[1] Download pretrained models "
    if [ ! -e "anon/pretrained_models_anon_xv/" ]; then
        cd anon
        if [ -f pretrained_models_anon_xv.tar.gz ];
        then
           rm pretrained_models_anon_xv.tar.gz
        fi
        echo -e "${RED}Downloading pre-trained model${NC}"

        wget https://zenodo.org/record/6529898/files/pretrained_models_anon_xv.tar.gz
        tar -xzvf pretrained_models_anon_xv.tar.gz

        #change the pretrained model path
        cp configs/libri_tts_clean_100_fbank_xv_ssl_freeze.json pretrained_models_anon_xv/HiFi-GAN/libri_tts_clean_100_fbank_xv_ssl_freeze/config.json
        
        cd pretrained_models_anon_xv/
        wget https://dl.fbaipublicfiles.com/hubert/hubert_base_ls960.pt
        
       cd $rootdir
	
    fi
fi


if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    echo "[2] Predict RTTM on original conversation, split conversation, predict gender for each speaker"
    bash sd/predict_rttm.sh data/wavs data/rttms exp/predict_rttm_ori
fi

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    echo "[3] Compute original speaker vector for each speaker "
    bash anon/selec_anon/compute_ori_spk_vector/extract_emb_fbank.sh 
fi

if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    echo "[4] Selction-base : compute anonymized speaker vector for each speaker "
    bash anon/selec_anon/compute_anon_spk_vector/compute_anon_select.sh
fi

if [ ${stage} -le 5 ] && [ ${stop_stage} -ge 5  ]; then
    echo "[5] AS and DS : compute anonymized speaker vector for each speaker "
    bash anon/anon_control/run.sh 
fi

if [ ${stage} -le 6 ] && [ ${stop_stage} -ge 6  ]; then
    echo "[6] generated res/select/as/ds speech "
    bash anon/scripts/engl_scripts/sd.sh
fi 

if [ ${stage} -le 7 ] && [ ${stop_stage} -ge 7  ]; then
    for type in res select ds as;do
        echo "[7] caculate DER for $type speech "
        bash sd/predict_rttm.sh exp/output_speech/predict_rttm/demo_$type data/rttms exp/predict_rttm_anon_$type
    done
fi
