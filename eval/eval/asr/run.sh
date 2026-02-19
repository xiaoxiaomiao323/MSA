#conda activate myenv
python predict.py /root/data/belinda/slue_select/cosyvoice cosyvoice.txt
python compute_wer.py --mode present ori_key.txt cosyvoice.txt 
#python predict.py /root/data/belinda/slue_select/valle_16k  valle_predict.txt
#python compute_wer.py --mode present ori_key.txt valle_predict.txt 

#python predict.py /root/data/belinda/slue_select/ori/  ori_predict.txt
#python compute_wer.py --mode present ori_key.txt ori_predict.txt 
#python predict.py /root/data/belinda/slue_select/xtts_16k_2/  xtts_predict_2.txt
#python compute_wer.py --mode present ori_key.txt xtts_predict_2.txt 
#python predict.py /root/data/belinda/slue_select/partertts_16k_mxx/  parler_predict_mxx.txt
#python compute_wer.py --mode present ori_key.txt parler_predict_mxx.txt 
