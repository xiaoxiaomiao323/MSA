#!/bin/bash
# ==============================================================================
# Copyright (c) 2024, Singapore Institute of Technology
# Author: Xiaoxiao Miao (xiaoxiao.miao@singaporetech.edu.sg)
# All rights reserved.
# ==============================================================================


source env.sh
LOGFILE="process.log"  # Define the log file
exec > >(tee -a "$LOGFILE") 2>&1  # Redirect stdout and stderr to the log file

stage=1
stop_stage=7
rootdir=$PWD

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then

    echo "[1.1] Download simulation evaluation data"
    if [ ! -d "msa_data/" ]; then
        if [ ! -f "msa_data.tar.gz" ]; then
	    wget  -q --show-progress https://zenodo.org/records/14249171/files/msa_data.tar.gz
	fi
	tar -xzf msa_data.tar.gz
    fi


    echo "[1.2] Download pretrained models"
    if [ ! -e "anon/pretrained_models_anon_xv/" ]; then
        cd anon
        if [ -f pretrained_models_anon_xv.tar.gz ];
        then
           rm pretrained_models_anon_xv.tar.gz
        fi
        echo -e "${RED}Downloading pre-trained model${NC}"

        wget -q --show-progress  https://zenodo.org/record/6529898/files/pretrained_models_anon_xv.tar.gz
        tar -xzf pretrained_models_anon_xv.tar.gz

        #change the pretrained model path
        cp configs/libri_tts_clean_100_fbank_xv_ssl_freeze.json pretrained_models_anon_xv/HiFi-GAN/libri_tts_clean_100_fbank_xv_ssl_freeze/config.json
        
        cd pretrained_models_anon_xv/
        wget https://dl.fbaipublicfiles.com/hubert/hubert_base_ls960.pt
        
       cd $rootdir
	
    fi
fi


for con in clean noise; do
    for num in spk2 spk3 spk4 spk5; do
        datadir=msa_data/$con/$num
	dset=${con}_${num}
	echo $datadir
        if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
            echo "[2] Predict RTTM on original conversation, split conversation, predict gender for each speaker"
            start_time=$(date +%s)
            bash sd/predict_rttm.sh $datadir/wavs $datadir/rttms exp/$dset/predict_rttm_ori
            end_time=$(date +%s)
            echo "Stage 2 completed in $((end_time - start_time)) seconds."
        fi

        if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
            echo "[3] Compute original speaker vector for each speaker"
            start_time=$(date +%s)
            bash anon/selec_anon/compute_ori_spk_vector/extract_emb_fbank.sh $dset
            end_time=$(date +%s)
            echo "Stage 3 completed in $((end_time - start_time)) seconds."
        fi

        if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
            echo "[4] Selection-based: compute anonymized speaker vector for each speaker"
            start_time=$(date +%s)
            bash anon/selec_anon/compute_anon_spk_vector/compute_anon_select.sh $dset
            end_time=$(date +%s)
            echo "Stage 4 completed in $((end_time - start_time)) seconds."
        fi

        if [ ${stage} -le 5 ] && [ ${stop_stage} -ge 5 ]; then
            echo "[5] AS and DS: compute anonymized speaker vector for each speaker"
            start_time=$(date +%s)
            bash anon/anon_control/run.sh $dset
            end_time=$(date +%s)
            echo "Stage 5 completed in $((end_time - start_time)) seconds."
        fi

        if [ ${stage} -le 6 ] && [ ${stop_stage} -ge 6 ]; then
            echo "[6] Generate res/select/as/ds speech"
            start_time=$(date +%s)
            bash anon/scripts/engl_scripts/sd.sh $dset
            end_time=$(date +%s)
            echo "Stage 6 completed in $((end_time - start_time)) seconds."
        fi

        if [ ${stage} -le 7 ] && [ ${stop_stage} -ge 7 ]; then
            echo "[7] Calculate DER for each type of speech"
            start_time=$(date +%s)
            for type in res select ds as; do
                echo "Calculating DER for $type speech"
                bash sd/predict_rttm.sh exp/output_speech/predict_rttm/${dset}_${type} $datadir/rttms exp/$dset/predict_rttm_${type}
            done

            for type in ori res select ds as; do
                echo "DER for $type speech"
                cat exp/$dset/predict_rttm_${type}/der
            done
            echo "Generated audio samples are saved under exp folder."
            end_time=$(date +%s)
            echo "Stage 7 completed in $((end_time - start_time)) seconds."
        fi
    done
done

