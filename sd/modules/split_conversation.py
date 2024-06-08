import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import re
import os,sys
audio_dir = sys.argv[1]
rttm_dir = sys.argv[2]
output_dir = sys.argv[3]
def normalize(signal1):
    try:
        intinfo = np.iinfo(signal1.dtype)
        return signal1 / max( intinfo.max, -intinfo.min )

    except ValueError: # array is not integer dtype
        return signal1 / max( signal1.max(), -signal1.min() )
    
for wavname in open(audio_dir):
    wavname = wavname.strip().split(' ')[-1]
    basename = os.path.basename(wavname)
    basename = basename.split('.')[0]
    basename = basename.replace('_gen','')
    rate, wavdata = read(wavname)


    speaker = []
    with open('%s/%s.rttm'%(rttm_dir,basename)) as f:
        line = f.readline()
        while line:
            temp = line.strip().split(' ')
            start = float(temp[3])
            length = float(temp[4])
            if '_' not in temp[7]:
                user = temp[1] + '_' + temp[7]
            else:
                user = temp[7]
            tmpdata = {"start":start, "length": length, "user":user}
            speaker.append(tmpdata)
            line = f.readline()
    sorted_data = sorted(speaker, key=lambda x: x['start'])

    curpos = 0
    dict_data = {}
    for item in sorted_data:
        start_pos = int(item["start"] * rate)
        data_length = int(item["length"] * rate)
        if item["user"] not in dict_data:
            dict_data[item["user"]] = []
        tmpdata = wavdata[start_pos:start_pos+data_length]
        dict_data[item["user"]].append(tmpdata)
    


    for key in dict_data:
        result = []
        for data in dict_data[key]:
            result = np.concatenate((result, data), axis=0)
        result = normalize(result)
        write("%s/%s.wav"%(output_dir, key),rate, result)


