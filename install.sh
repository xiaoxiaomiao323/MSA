#!/bin/bash
# ==============================================================================
# Copyright (c) 2024, Singapore Institute of Technology
# Author: Xiaoxiao Miao (xiaoxiao.miao@singaporetech.edu.sg)
# All rights reserved.
# ==============================================================================

set -e


conda_url=https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh
venv_dir=$PWD/venv

mark=.done-venv
if [ ! -f $mark ]; then
  echo 'Making python virtual environment'
  name=$(basename $conda_url)
  if [ ! -f $name ]; then
    wget $conda_url || exit 1
  fi
  [ ! -f $name ] && echo "File $name does not exist" && exit 1
  [ -d $venv_dir ] && rm -r $venv_dir
  sh $name -b -p $venv_dir || exit 1
  . $venv_dir/bin/activate
  echo 'Installing python dependencies'
  CUDA_VERSION=11.3
  TORCH_VERSION=1.11.0
  cuda_version_without_dot=$(echo $CUDA_VERSION | xargs | sed 's/\.//')

  version="==$TORCH_VERSION+cu$cuda_version_without_dot"
  echo -e "\npip3 install torch$version torchvision torchaudio --force-reinstall --index-url https://download.pytorch.org/whl/${nightly}cu$cuda_version_without_dot\n"
  pip3 install torch$version torchvision torchaudio --force-reinstall --index-url https://download.pytorch.org/whl/${nightly}cu$cuda_version_without_dot \


  pip install -r requirements.txt || exit 1
  touch $mark
fi
echo "if [ \"\$(which python)\" != \"$venv_dir/bin/python\" ]; then source $venv_dir/bin/activate; fi" > env.sh
