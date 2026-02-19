import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torchaudio
from speechbrain.pretrained import EncoderClassifier
from sklearn.metrics.pairwise import cosine_distances
import pandas as pd

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",run_opts={"device": device} )
def extract_vector(audio):
        signal, fs =torchaudio.load(audio)
        return classifier.encode_batch(wavs=signal).squeeze(0)


def extract_vector_pair(audio):
        signal, fs =torchaudio.load(audio)
        length = signal.shape[-1]
        signal1 = signal[:, :int(length/2)]
        signal2 = signal[:, int(length/2):]

        return classifier.encode_batch(wavs=signal1).squeeze(0), classifier.encode_batch(wavs=signal2).squeeze(0)



# functions to get EERs
def compute_det_curve(target_scores, nontarget_scores):
    """ 
    frr, far, thr = comcompute_eercurve(target_scores, nontarget_scores)
    
    input
    -----
      target_scores:    np.array, target trial scores
      nontarget_scores: np.array, nontarget trial scores 

    output
    ------
      frr:   np.array, FRR, (#N, ), where #N is total number of scores + 1
      far:   np.array, FAR, (#N, ), where #N is total number of scores + 1
      thr:   np.array, threshold, (#N, )
    
    """
    
    n_scores = target_scores.size + nontarget_scores.size
    all_scores = np.concatenate((target_scores, nontarget_scores))
    labels = np.concatenate((np.ones(target_scores.size), 
                             np.zeros(nontarget_scores.size)))

    # Sort labels based on scores
    indices = np.argsort(all_scores, kind='mergesort')
    labels = labels[indices]

    # Compute false rejection and false acceptance rates
    tar_trial_sums = np.cumsum(labels)
    nontarget_trial_sums = (nontarget_scores.size - 
                            (np.arange(1, n_scores + 1) - tar_trial_sums))

    frr = np.concatenate((np.atleast_1d(0), tar_trial_sums/target_scores.size))
    # false rejection rates
    far = np.concatenate((np.atleast_1d(1), 
                          nontarget_trial_sums / nontarget_scores.size))  
    # false acceptance rates
    thresholds = np.concatenate((np.atleast_1d(all_scores[indices[0]] - 0.001), 
                                 all_scores[indices]))  
    # Thresholds are the sorted scores
    return frr, far, thresholds


def compute_eer(target_scores, nontarget_scores):
    """
    eer, eer_threshold = compute_eer(target_scores, nontarget_scores)
    
    input
    -----
      target_scores:    np.array, or list of np.array, target trial scores
      nontarget_scores: np.array, or list of np.array, nontarget trial scores 

    output
    ------
      eer:            float, EER 
      eer_threshold:  float, threshold corresponding to EER
    
    """
    if type(target_scores) is list and type(nontarget_scores) is list:
        frr, far, thr = compute_det_curve(target_scores, nontarget_scores)
    else:
        frr, far, thr = compute_det_curve(target_scores, nontarget_scores)
    
    # find the operation point for EER
    abs_diffs = np.abs(frr - far)
    min_index = np.argmin(abs_diffs)

    # compute EER
    eer = np.mean((frr[min_index], far[min_index]))    
    return eer, thr[min_index]


def compute_far(scores, threshold):
    """
    far = compute_far(scores, threshold)
    
    Compute false acceptance rate
    
    input
    -----
      scores:    np.array, or list of np.array, trial scores
      threshold: float, threshold for decision

    output
    ------
      far:            float, false acceptance rate
    """
    return np.sum(scores > threshold) / scores.size


def _find_audio(path_base):
    """Find audio file: try .ogg first, then .wav (for sample data)."""
    for ext in ('.ogg', '.wav'):
        p = path_base + ext
        if os.path.isfile(p):
            return p
    return path_base + '.ogg'


def gen_pos_neg(file_path, out_dir=None):
  # Read the TSV file, specifying the columns we are interested in
  df = pd.read_csv(file_path, sep='\t', usecols=['id', 'speaker_id'])

  # Remove rows where speaker_id is None
  df = df[df['speaker_id'].notna()]

  # Initialize lists to store positive and negative pairs
  positive_pairs = []
  negative_pairs = []

  # Convert the DataFrame to a list of tuples for easier iteration
  records = df.to_records(index=False)
  record_list = list(records)

  # Generate pairs
  for i in range(len(record_list)):
      for j in range(i + 1, len(record_list)):
          id1, speaker_id1 = record_list[i]
          id2, speaker_id2 = record_list[j]
          
          if speaker_id1 == speaker_id2:
              positive_pairs.append((id1, id2))
          else:
              negative_pairs.append((id1, id2))
  
  # Optionally write trials to out dir (not to cwd)
  if out_dir:
      trials_path = os.path.join(out_dir, 'trials.txt')
      with open(trials_path, 'w') as f:
          for pair in positive_pairs:
              f.write(f"{pair[0]} {pair[1]} 1\n")
          for pair in negative_pairs:
              f.write(f"{pair[0]} {pair[1]} 0\n")

  return  positive_pairs, negative_pairs


input_key = sys.argv[1]
ori_dir = sys.argv[2]
anon_dir = sys.argv[3]
out = sys.argv[4]
positive_pairs, negative_pairs = gen_pos_neg(input_key, out)
# Choose a subset
positive_pairs = positive_pairs[:1000]
negative_pairs = negative_pairs[:1000]
neg = []
pos = []
oa = []

print(len(positive_pairs), len(negative_pairs))

for pos_pair in positive_pairs:
  id1 = pos_pair[0]
  id2 = pos_pair[1]

  line_spks = []
  wav1 = _find_audio(ori_dir + '/' + id1)
  wav2 = _find_audio(ori_dir + '/' + id2)
  wav3 = anon_dir + '/' + id2 + '.wav'

  vector1 = extract_vector(wav1).cpu().numpy()
  vector2 = extract_vector(wav2).cpu().numpy()
  vector3 = extract_vector(wav3).cpu().numpy()

  distance_array = cosine_distances(vector1, vector2)[0, 0]
  cosine_distance = 1 - float(distance_array)  # Assuming distance_array is a single value
  pos.append(cosine_distance)

  dis2 = cosine_distances(vector1, vector3)[0, 0]
  cos2 = 1 - float(dis2)  # Assuming distance_array is a single value
  oa.append(cos2)


for neg_pair in negative_pairs:
  id1 = neg_pair[0]
  id2 = neg_pair[1]
  line_spks = []
  wav1 = _find_audio(ori_dir + '/' + id1)
  wav2 = _find_audio(ori_dir + '/' + id2)
  vector1 = extract_vector(wav1).cpu().numpy()
  vector2 = extract_vector(wav2).cpu().numpy()
  distance_array = cosine_distances(vector1, vector2)[0, 0]
  cosine_distance = 1 - float(distance_array)  # Assuming distance_array is a single value
  neg.append(cosine_distance)



pos = np.array(pos)
neg = np.array(neg)
oa = np.array(oa)

np.save('%s/pos.npy'%out, pos)
np.save('%s/neg.npy'%out, neg)
np.save('%s/oa.npy'%out, oa)

pos = np.load('%s/pos.npy'%out)
neg = np.load('%s/neg.npy'%out)
oa = np.load('%s/oa.npy'%out)

_, threshold = compute_eer(pos, neg)
far = compute_far(oa, threshold)
print('False acceptance rate: {:.2f}'.format(far * 100))


# Show far value on the plot
plt.text(0.05, 0.95, f'FAR: {far*100:.2f}%', ha='left', va='top', transform=plt.gca().transAxes,
         fontsize=20, bbox=dict(facecolor='none', edgecolor='none', alpha=0.0))

plt.hist(pos, color='r', density=True, alpha=0.3);
plt.hist(neg, color='b', density=True, alpha=0.3);
plt.hist(oa, color='y', density=True, alpha=0.3);
plt.plot([threshold, threshold], [0, 0.5], color='k');
# Set x and y axis ranges
plt.xlim([-0.2, 1])
plt.ylim([0, 5])
base = out.split('/')[-1]
plt.savefig('%s/%s.png'%(out,base))
