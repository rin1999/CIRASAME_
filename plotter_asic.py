'''
指定したASICの全32チャンネルを重ね書きする
'''

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import re
import glob
import numpy as np
import statistics
#from scipy.optimize import curve_fit

parser = argparse.ArgumentParser()
parser.add_argument('-a','--asic', default='1')
parser.add_argument('-f', '--file')
args = parser.parse_args()

READ_ASIC = int(args.asic)
#print(READ_ASIC)
read_row = []
read_col = []
for i in range(32):
    read_ch = 32*(READ_ASIC-1) + i
    read_row.append(int((read_ch+10)/4))
    read_col.append(int(read_ch+10)%4)

print(read_row)

DIR_PATH = 'data/'+args.file+'/decimal'
file_list = glob.glob(os.path.join(DIR_PATH, "*.txt"))

hits = [[] for _ in range(32)]
dac_val = []

#print(READ_CH)

for file_path in file_list:
    file_name = os.path.basename(file_path)
    #print('now reading '+file_name)
    v_dac = int(re.sub(r"\D", "", file_name))
    df = pd.read_table(file_path, sep='\s+', header=None)

    #3rd word が１カウント当たり0.524ms
    t=0
    try:
        t = (df.iat[0,3]+1)*0.524*0.001
    except:
        continue
    
    for i in range(32):
        if df.iat[read_row[i], read_col[i]+1] == 0:
            hits[i].append(np.log10(1/t))
        else:
            hits[i].append(np.log10(df.iat[read_row[i], read_col[i]+1]/t))
    dac_val.append(v_dac)

y_max = []
y_min = []
y_ave = []

for i in range(len(dac_val)):
    pool = []
    for j in range(32):
        pool.append(hits[j][i])
    y_max.append(max(pool))
    y_min.append(min(pool))
    y_ave.append(statistics.mean(pool))

y_top = []
y_bottom = []
for i in range(len(dac_val)):
    y_top.append(y_max[i]-y_ave[i])
    y_bottom.append(y_ave[i]-y_min[i])

#plt.scatter(dac_val,y_max)
#plt.scatter(dac_val,y_min)
#plt.scatter(dac_val,y_ave)
y_err = [y_bottom,y_top]
plt.errorbar(dac_val,y_ave,yerr=y_err, fmt='o')

#print(df)
#for i in range(32):
#    plt.scatter(dac_val, hits[i])

plt.xlabel('threshold (DAC value)')
plt.ylabel('count per second (log_10)')
plt.grid(True)
plt.savefig('pic/{}_asic{}.png'.format(args.file,args.asic))
#plt.show()
