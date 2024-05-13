import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import re
import glob
import numpy as np
#from scipy.optimize import curve_fit

parser = argparse.ArgumentParser()
parser.add_argument('-ch','--channel', default='0')
parser.add_argument('-f', '--file')
args = parser.parse_args()

READ_CH = int(args.channel)
READ_CH = READ_CH + 10
read_row = int(READ_CH/4)
read_col = READ_CH%4

DIR_PATH = 'data/'+args.file+'/decimal'
file_list = glob.glob(os.path.join(DIR_PATH, "*.txt"))

hits = []
dac_val = []

#print(READ_CH)

for file_path in file_list:
    file_name = os.path.basename(file_path)
    #print('now reading '+file_name)
    v_dac = int(re.sub(r"\D", "", file_name))
    df = pd.read_table(file_path, sep='\s+', header=None)

    #3rd word が１カウント当たり0.524ms
    t = df.iat[0,3]*0.524*0.001
    if t == 0:
        continue
    #hits.append(df.iat[read_row+2, read_col+1]/clock*125000000)
    if df.iat[read_row, read_col+1] == 0:
        hits.append(np.log10(1/t))
    else:
        hits.append(np.log10(df.iat[read_row, read_col+1]/t))
    dac_val.append(v_dac)

"""
def sigmoid_func(x, x0, a, b, c): #for fitting
    #if x<0:
        return a/(1+np.exp(-b*(x-x0))) + c
    #else:
    #    return np.exp(a*(x-x0))/(np.exp(a*(x-x0))+1)
"""
#print(df)

plt.scatter(dac_val, hits)
#plt.yscale('log')
plt.xlabel('threshold (DAC value)')
plt.ylabel('count per second (log_10)')
plt.grid(True)
plt.show()
