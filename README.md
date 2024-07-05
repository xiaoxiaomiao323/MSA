# MSA

## A Benchmark for Multi-speaker Anonymization 

This is an implementation of the paper - A Benchmark for Multi-speaker Anonymization

The authors are Xiaoxiao Miao, Ruijie Tao, Chang Zeng, Xin Wang.


Audio samples can be found here: https://xiaoxiaomiao323.github.io/msa-audio/

## Dependencies

`git clone https://github.com/xiaoxiaomiao323/MSA.git`

`cd MSA`

`bash install.sh`

`bash demo.sh`

## Demo Results
Three randomly selected conversations with 3, 4, and 5 speakers respectively are anonymized using different MSAs.
|                  | DER  | FA  | MS  | SC  |
|------------------|------|-----|-----|-----|
| Original         | 5.54 | 0.00| 0.00| 5.54|
| Resynthesized    | 7.28 | 0.20| 0.17| 6.91|
|  $A_{selec}$  | 6.05 | 0.00| 0.00| 6.05|
| $A_{ds}$     | 6.49 | 0.43| 0.00| 6.06|
| $A_{as}$    | 6.06 | 0.00| 0.00| 6.06|

## Acknowledgments
This study is partially supported by JST, PRESTO Grant Number JPMJPR23P9, Japan and SIT-ICT Academic Discretionary Fund.

## License

The `anon/adapted_from_facebookreaserch` subfolder has [Attribution-NonCommercial 4.0 International License](https://github.com/xiaoxiaomiao323/MSA/blob/main/anon/adapted_from_facebookresearch/LICENSE). The `anon/adapted_from_speechbrain` subfolder has [Apache License](https://github.com/xiaoxiaomiao323/MSA/blob/main/anon/adapted_from_speechbrain/LICENSE). They were created by the [facebookreasearch](https://github.com/facebookresearch/speech-resynthesis/blob/main) and [speechbrain](https://github.com/speechbrain/speechbrain) orgnization, respectively. The `anon/scripts` and `anon
/anon_control` subfolder has the [MIT license](https://github.com/nii-yamagishilab/SSL-SAS/blob/main/scripts/LICENSE).

Because this source code was adapted from the facebookresearch and speechbrain, the whole project follows  
the [Attribution-NonCommercial 4.0 International License](https://github.com/nii-yamagishilab/SSL-SAS/blob/main/adapted_from_facebookresearch/LICENSE).


