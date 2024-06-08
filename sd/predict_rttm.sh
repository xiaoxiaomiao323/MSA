stage=1
stop_stage=8

audio_dir=$1
label_dir=$2
exp=$3

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    echo "[1] Process dataset"
    mkdir -p $exp
    ls ${audio_dir}/*.wav | awk -F/ '{print substr($NF, 1, length($NF)-4), $0}' > $exp/wav_mix.scp
fi


if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    min_duration=0.255
    echo "[2] VAD"
    python sd/modules/vad.py \
            --repo-path sd/external_tools/silero-vad-3.1 \
            --scp $exp/wav_mix.scp \
            --threshold 0.17 \
            --min-duration $min_duration > $exp/vad
fi


if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    echo "[3] Extract and cluster"
    python sd/modules/cluster.py \
            --scp $exp/wav_mix.scp \
            --segments $exp/vad \
            --source sd/pretrained_models/cam-vox2.model \
            --output $exp/vad_labels
fi


if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    echo "[4] Get RTTM"
    python sd/modules/make_rttm.py \
            --labels $exp/vad_labels \
            --channel 1  > $exp/res_rttm_o
fi

if [ ${stage} -le 5 ] && [ ${stop_stage} -ge 5 ]; then    
    echo "[5] Re-order and get DER result"
    python sd/modules/re_order_rttm.py -f $exp/res_rttm_o > $exp/res_rttm
    cat ${label_dir}/*.rttm > $exp/all.rttm
    perl sd/external_tools/SCTK-2.4.12/src/md-eval/md-eval.pl -c 0.25 -r $exp/all.rttm -s $exp/res_rttm > $exp/der
    cat $exp/der
    python sd/modules/change_rttm_seperate.py $exp/res_rttm
fi


if [ ${stage} -le 6 ] && [ ${stop_stage} -ge 6 ]; then    
    echo "[6] split conversation"
    rm -rf $exp/wav_sep
    mkdir -p $exp/wav_sep
    python sd/modules/split_conversation.py $exp/wav_mix.scp $exp/rttms $exp/wav_sep
fi


if [ ${stage} -le 7 ] && [ ${stop_stage} -ge 7 ]; then
    echo "[7] predict gender"
    python sd/modules/test_gender.py $exp/wav_sep $exp/gender.txt
fi


if [ ${stage} -le 8 ] && [ ${stop_stage} -ge 8 ]; then
    echo "[8] generate kaldi-format datasets"
    ls `pwd`/$exp/wav_sep/*.wav | awk -F/ '{print substr($NF, 1, length($NF)-4), $0}' > $exp/wav.scp
    python sd/modules/gen_scp.py $exp/wav.scp $exp/gender.txt $exp/

fi
