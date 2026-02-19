#!/bin/bash
#SBATCH --gres=gpu:tesla_a100:1
#SBATCH --time=3-00:00:00
#SBATCH -w gpuhost13
#SBATCH --cpus-per-gpu=4
module load cuda11.1

MAIN_ROOT=/home/smg/miao/anaconda3/envs/pytorch-1.8
if [ $(which python) != $MAIN_ROOT/bin/python ]; then source /home/smg/miao/anaconda3/bin/activate pytorch-1.8; fi
data_dir=/home/smg/miao/provided/mos_predict/resample_norm/wav_norm
dset=B1_libri_dev_enrolls

python run_inference_for_challenge.py --datadir $data_dir/$dset 
echo The individual scores are save in answer_${dset}.txt


echo  The mean of answer_$dset.txt is 
awk '{ total += $2; count++ } END { print total/count }' answer_${dset}.txt 
