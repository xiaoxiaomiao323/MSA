#coding=utf-8
import os,sys
import numpy as np
from kaldiio import ReadHelper
import kaldi_io


def write_raw_mat(data,filename,format='f4',end='l'):
    """write_raw_mat(data,filename,format='',end='l')
       Write the binary data from filename.
       Return True

       data:     np.array
       filename: the name of the file, take care about '\\'
       format:   please use the Python protocal to write format
                 default: 'f4', float32
       end:      little endian 'l' or big endian 'b'?
                 default: '', only when format is specified, end
                 is effective

       dependency: numpy
       Note: we can also write two for loop to write the data using
             f.write(data[a][b]), but it is too slow
    """
    if not isinstance(data, np.ndarray):
        print("Error write_raw_mat: input shoul be np.array")
        return False
    f = open(filename,'wb')
    if len(format)>0:
        if end=='l':
            format = '<'+format
        elif end=='b':
            format = '>'+format
        else:
            format = '='+format
        datatype = np.dtype((format,1))
        temp_data = data.astype(datatype)
    else:
        temp_data = data
    temp_data.tofile(f,'')
    f.close()
    return True

def cosine(vec1, vec2):
    return np.sum(vec1 * vec2) / np.sqrt(np.sum(vec1*vec1) * np.sum(vec2*vec2))

def norm(vec):
    return vec/np.sqrt(np.sum(vec * vec))

def load_scp(scp_file):
    pool_xvectors = {}
    c = 0
    with ReadHelper('scp:' + scp_file) as reader:
        for key, xvec in reader:
            if xvec.shape[0] == 1:
                xvec = xvec[0,:]
            pool_xvectors[key] = xvec
            c += 1
        print("Read ", c, "xvectors")
    return pool_xvectors

def load_gender(spk2gender_file):
    spk2gender = {}
    with open(spk2gender_file) as f:
        for line in f.read().splitlines():
            sp = line.split()
            spk2gender[sp[0]] = sp[1]
    return spk2gender


pool_m = sys.argv[1]
pool_f = sys.argv[2]
data_path = sys.argv[3]
gender = sys.argv[4]
out_full_dir = sys.argv[5]

if not os.path.exists(out_full_dir):
    os.makedirs(out_full_dir)

pool_m_data = load_scp(pool_m)
pool_f_data = load_scp(pool_f)


target_data = {}
target_gender = {}
i = 0
target_idx = {}
for key in pool_m_data:
    target_data[key] = pool_m_data[key]
    target_gender[key] = "M"
    target_idx[i] = key
    i += 1
    
for key in pool_f_data:
    target_data[key] = pool_f_data[key]
    target_gender[key] = "F"
    target_idx[i] = key
    i += 1
i = 0
target_gender_idx = {}


for key in target_data:
    target_gender_idx[i] = target_gender[key]
    i += 1

input_data = load_scp(data_path)
input_gender = load_gender(gender)

spk_all = {}
for key in input_data:
    spk = "_".join(key.split("_")[0:-1])
    if spk not in spk_all:
        spk_all[spk] = []
    spk_all[spk].append((key, norm(input_data[key]), input_gender[key]))


center = target_data
i = 0
center_mat = np.zeros((len(center), 192))
for key in center.keys():
    center_mat[i] = norm(center[key])
    i += 1
target_sim = np.dot(center_mat, center_mat.T)   #compute similarity matrix for pool data


for spk_key in spk_all:   
    data_tmp = spk_all[spk_key]
    spk_num = len(data_tmp)
    input_data_tmp = np.zeros((spk_num, 192))
    for i in range(spk_num):
        input_data_tmp[i] = data_tmp[i][1]
    
    imput_sim = np.dot(input_data_tmp, input_data_tmp.T)    #compute similarity matrix for input data
    cross_sim = np.dot(input_data_tmp, center_mat.T)       #compute similarity matrix for input-pool data
    

    top_p = 200
    th = 1
    
    import itertools
    lists = []
    for i in range(spk_num):
        # Protecting privacy
        # choose the same-gender pool with input speaker, ensure the gender of each speaker remains the same before and after anonymization.
        # for each speaker, choose top_p furthest speaker vectors from pool as candidate speaker vectors
        gender = data_tmp[i][2]
        #print(gender)
        if gender == "M":
            flat_indices_1 = np.argsort(cross_sim[i][:560])[:top_p] 
            flat_indices_2 = np.where(cross_sim[i][:560] < th)[0]
            
            lists.append(list(set(flat_indices_1) & set(flat_indices_2)))
        else:
            flat_indices_1 = np.argsort(cross_sim[i][560:])[:top_p] + 560
            flat_indices_2 = np.where(cross_sim[i][560:] < th)[0] + 560
            
            lists.append(list(set(flat_indices_1) & set(flat_indices_2)))
    
    # Maintaining utility
    scores = {0 : []} # Buffer to save external candidate speaker index and similarity
    for key in lists[0]:
        scores[0].append(([key], 0))
      
    for idx in range(1, spk_num):
        scores[idx] = []
        for key in lists[idx]:  # key: possibel speaker vector choice for current speaker 
            for key1 in scores[idx-1]: # key1: a list of speaker indices and represents one possible speaker vector choice for previous idx-1 speakers}
                scores_tmp = key1[1] 
                for j in key1[0]:
                    scores_tmp += target_sim[j, key] #  the aggretated similarity score
                scores[idx].append((key1[0] + [key], scores_tmp))
         # update the statistics and keep the 10,000 choices with the smallest similarities
        n = 10000
        tmp = sorted(scores[idx], key=lambda x: x[1])
        scores[idx] = tmp[:min(n, len(tmp))]
    
    """
    tmp_sim = np.zeros((spk_num, spk_num)) 
    for i in range(spk_num):
        for j in range(spk_num):
           tmp_sim[i, j] =  target_sim[scores[spk_num-1][0][0][i], scores[spk_num-1][0][0][j]]
    """
    #Retrieve the index for each speaker
    tmp = [target_idx[key] for key in scores[spk_num-1][0][0]]
    for index, nn in enumerate(tmp):
        index = index +1 
        out_path_name = out_full_dir + '/' + spk_key + '_speaker' + str(index) + '.xvector'
        write_raw_mat(target_data[nn], out_path_name)
    #print(spk_key, tmp, scores[spk_num-1][0][1])









        

    
                

    


    
    
    






