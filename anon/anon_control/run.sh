#!/bin/bash
# ==============================================================================
# Copyright (c) 2024, Singapore Institute of Technology
# Author: Xiaoxiao Miao (xiaoxiao.miao@singaporetech.edu.sg)
# All rights reserved.
# ==============================================================================

pool=anon/selec_anon/output_anon_spk_vector/libritts_train_other_500
pool_gender=anon/data/libritts_train_other_500/spk2gender
pool_m=$pool/spk_xvector_m_avg.scp
pool_f=$pool/spk_xvector_f_avg.scp
xvdir=anon/selec_anon/output_ori_spk_vector
datadir=anon/data


echo anonymize speaker vector pool 
python anon/anon_control/ceter_avg.py $pool/spk_xvector.scp ${pool_gender} ${pool_m} ${pool_f}



dset=$1
for type in as ds; do
    echo using $type loss to search anonymized speaker vector for $1
    start_time=$(date +%s)
    outdir=anon/anon_control/exp/$type/
    python anon/anon_control/$type.py ${pool_m} ${pool_f} \
        $xvdir/${dset}/xvector.scp \
        $datadir/${dset}/spk2gender \
	anon/anon_control/exp/$type/${dset}
    end_time=$(date +%s)
    echo "$type of $1 completed in $((end_time - start_time)) seconds."
done

