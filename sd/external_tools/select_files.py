import subprocess

select_list = "/workspace/SID_related/anti_diar/select.lst"
data_path = "/home/user/data08/voxconverse/full/"
new_path = "/home/user/data08/voxconverse/select/"

lines = open(select_list).read().splitlines()
for line in lines:
    orig_audio_file = data_path + 'audio/' + line
    new_audio_file = new_path + 'audio/' + line
    cmd = "scp %s %s"%(orig_audio_file, new_audio_file)
    subprocess.call(cmd, shell=True, stdout=None)
    
    orig_label_file = data_path + 'label/' + line.replace('.wav', '.rttm')
    new_label_file = new_path + 'label/' + line.replace('.wav', '.rttm')
    cmd = "scp %s %s"%(orig_label_file, new_label_file)
    subprocess.call(cmd, shell=True, stdout=None)