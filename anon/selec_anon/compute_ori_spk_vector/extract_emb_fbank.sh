#!/bin/bash
# ==============================================================================
# Copyright (c) 2024, Singapore Institute of Technology
# Author: Xiaoxiao Miao (xiaoxiao.miao@singaporetech.edu.sg)
# All rights reserved.
# ==============================================================================


source ./env.sh
config=anon/configs/extract_ecapa_f_ecapa_vox.yaml
echo ${config}
## extract libritts_train_other_500
source_dir=data
outdir=anon/selec_anon/output_ori_spk_vector
anon_pool="libritts_train_other_500"
xv_flag=provide
if [[ ${xv_flag} == "extract" ]]; then
	#compute original speaker vector for libritts_train_other_500 by yourself
	python anon/selec_anon/compute_ori_spk_vector/extract_emb.py ${config} $source_dir/$anon_pool/wav.scp $outdir/$anon_pool fbank
 elif [[ ${xv_flag} == 'provide' ]]; then
	echo download original speaker vector of libritts_train_other_500 as an external pool 
	cd anon
	BASE=$(pwd)
	echo $BASE
	if [ ! -e "libritts_train_other_500_xvector.tar.gz" ]; then
		wget https://github.com/nii-yamagishilab/SSL-SAS/releases/download/provided_xvector/libritts_train_other_500_xvector.tar.gz
	fi
	 tar -xvf  libritts_train_other_500_xvector.tar.gz
	 sed -i "s|selec_anon/output_ori_spk_vector/libritts_train_other_500/|$BASE/selec_anon/output_ori_spk_vector/libritts_train_other_500/|g" selec_anon/output_ori_spk_vector/libritts_train_other_500/xvector.scp

	 cd ../
fi


echo extract original vector for $1
dset=$1

python anon/selec_anon/compute_ori_spk_vector/extract_emb.py ${config} exp/$1/predict_rttm_ori/wav.scp $outdir/$dset fbank
mkdir -p anon/data/$dset
ln -sr exp/$dset/predict_rttm_ori/* anon/data/$dset/

