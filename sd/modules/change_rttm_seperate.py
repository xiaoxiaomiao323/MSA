import sys, os

input_rttm = sys.argv[1]
output_dir = os.path.join(os.path.dirname(input_rttm),'rttms')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

spk_rttm = {}
# Process input data
for line in open(input_rttm):
    temp = line.strip().split(' ')
    #last_field = "-".join(temp[-3].split('-')[:2])
    #print(last_field)
    #modified_line = ' '.join(temp[:-3]) + ' '+ last_field + ' <NA> <NA>'
    modified_line = line.strip()
    if temp[1] not in spk_rttm:
        spk_rttm[temp[1]] = []
    spk_rttm[temp[1]].append(modified_line)

for pattern, lines in spk_rttm.items():
    output_file_name = f"{output_dir}/{pattern}.rttm"
    with open(output_file_name, 'w') as output_file:
        for line in lines:
            output_file.write('%s\n'%line)
print("Files created successfully.")
