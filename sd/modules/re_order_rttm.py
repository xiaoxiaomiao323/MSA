
import argparse
from collections import defaultdict
import re

def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', help='original rttm file')
    parser.add_argument('-o', help='rttm file with the new order')
    args = parser.parse_args()

    return args


def main():
    args = get_args()



    lines = open(args.f).read().splitlines()
    Dic_num = defaultdict(int)
    for line in lines:
        data = line.split()
        file_name = data[1]
        temp = data[-3]
        speaker_id = int(re.search(r'\d+$',temp).group())
        Dic_num[file_name] = max(Dic_num[file_name], int(speaker_id))
    sorted_order = []
    for key in Dic_num:
        for i in range(Dic_num[key]):
            sorted_order.append("%s-speaker%d"%(key, i+1))
    
    old_order = {}
    Dic = defaultdict(int)
    for line in lines:
        data = line.split()
        file_name = data[1]
        speaker_id = data[-3]
        start_time = float(data[3])
        total_name = Dic_num[file_name]
        if "%s-%s"%(file_name, speaker_id) not in Dic:
            Dic["%s-%s"%(file_name, speaker_id)] = start_time

    for i in range(len(Dic.keys())):
        old_order[list(Dic.keys())[i]] = sorted_order[i]

    for line in lines:
        data = line.split()
        file_name = data[1]
        speaker_id = data[-3]
        new_speaker_id = old_order["%s-%s"%(file_name, speaker_id)].split('-')[-1]
        #new_line = data[0] + ' ' + data[1] + ' ' + data[2] + ' ' + data[3] + ' ' + data[4] + ' ' + data[5] + ' ' + data[6] + ' ' + new_speaker_id + ' ' + data[8] + ' ' + data[9]
        new_line = data[0] + ' ' + data[1] + ' ' + data[2] + ' ' + data[3] + ' ' + data[4] + ' ' + data[5] + ' ' + data[6] + ' ' + data[1]+'_'+new_speaker_id + ' ' + data[8] + ' ' + data[9]
        
        print(new_line)

if __name__ == '__main__':
    main()
