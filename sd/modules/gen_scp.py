import sys,os
wav_scp = sys.argv[1]
gender_predict = sys.argv[2]
out_dir = sys.argv[3]
fp_utt2spk = open('%s/utt2spk'%out_dir, 'w')
fp_spk2utt = open('%s/spk2utt'%out_dir, 'w')
for line in open(wav_scp):
    token = line.strip().split(' ')
    fp_utt2spk.write('%s %s\n'%(token[0], token[0]))
    fp_spk2utt.write('%s %s\n'%(token[0], token[0]))
fp_utt2spk.close()
fp_spk2utt.close()

fp_spk2gender = open('%s/spk2gender'%out_dir, 'w')
gender_map = {'female': 'F', 'male': 'M' }
for line in open(gender_predict):
    temp = line.strip().split('--')[-1]
    token = temp.split('.')[0]
    gender = gender_map[temp.split(' ')[-1]]
    fp_spk2gender.write('%s %s\n'%(token, gender))
fp_spk2gender.close()

    

