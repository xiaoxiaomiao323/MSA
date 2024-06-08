import os,sys
import numpy as np
from kaldiio import WriteHelper, ReadHelper
import kaldi_io
from sklearn.metrics.pairwise import cosine_similarity


def cosine(vec1, vec2):
    return np.sum(vec1 * vec2) / np.sqrt(np.sum(vec1*vec1) * np.sum(vec2*vec2))

def load_scp(scp_file):
    pool_xvectors = {}
    c = 0
    with ReadHelper('scp:' + scp_file) as reader:
        for key, xvec in reader:
            #print key, mat.shape
            pool_xvectors[key] = xvec[0, :]
            c += 1
        print("Read ", c, "pool xvectors")
    return pool_xvectors

def write_scp(data_dic, output_file_path):
    output_file_path = os.path.splitext(output_file_path)[0]
    print("Writing to: " + output_file_path)
    ark_scp_output = 'ark,scp:{:s}.ark,{:s}.scp'.format(
        output_file_path, output_file_path)
    with WriteHelper(ark_scp_output) as writer:
        for spk, xvec in data_dic.items():
            writer(spk, xvec)
    return

def load_gender(spk2gender_file):
    spk2gender = {}
    with open(spk2gender_file) as f:
        for line in f.read().splitlines():
            sp = line.split()
            spk2gender[sp[0]] = sp[1]
    return spk2gender

def norm(vec):
    return vec/np.sqrt(np.sum(vec * vec))



def find_min_sim(dict_data):
    # Compute cosine similarity for each pair of vectors
    cos_similarities = {}
    dict_data_avg = {}
    for spk1, vec1 in dict_data.items():
        #print(spk1)
        dict_data_avg[spk1] = vec1
        cos_similarities = {}
        for spk2, vec2 in dict_data.items():
            if spk1 != spk2:  # Avoid comparing the same vectors
                similarity = cosine_similarity([vec1], [vec2])[0][0]
                cos_similarities[(spk1, spk2)] = similarity
    
        top_10_max_similarities = sorted(cos_similarities.items(), key=lambda x: x[1], reverse=True)[:10]
        #print("Top 10 maximum similarities and the speakers involved:")
        #print(top_10_max_similarities)
        #average the ten most similar gender-consistent speaker vectors along with the original pool speaker vector itself to generate a replacement for  pool speaker vector.

        for pair, similarity in top_10_max_similarities:
            dict_data_avg[spk1] = dict_data_avg[spk1] + dict_data[pair[1]]
    return dict_data_avg

center_data = sys.argv[1]
center = load_scp(center_data)

gender_data = sys.argv[2]
spk_gender = load_gender(gender_data)

center_f = {}
center_m = {}
for spk, gender in spk_gender.items():
        #print(spk,gender)
        if spk not in center:
            #print(spk)
            continue
        if gender == 'F':
            center_f[spk] = center[spk]
        else:
            center_m[spk] = center[spk]


center_m_avg = find_min_sim(center_m)
write_scp(center_m_avg, sys.argv[3])

center_f_avg = find_min_sim(center_f)
write_scp(center_f_avg, sys.argv[4])
    

