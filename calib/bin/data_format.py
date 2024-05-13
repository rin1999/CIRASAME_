'''
Generates dat file from data
Usage:
1.  print all 128ch             ->  fill the -f argument(file name of data dir) only.
2.  print all 32ch in asic x    ->  fill the --asic argument(asic No 1~4) in addition to -f argument.

The data structure will be :
(example : 'python3 generate_datfile.py -f hoge')
'DAC_value' 'ch0'   'ch1'    ...    'ch126'  'ch127'  
124         1       8        ...    12       88 
126
...     

2024.04.19  R.Okazaki
'''


import pandas as pd
import argparse
import os
import re
import glob


parser = argparse.ArgumentParser()
parser.add_argument('--inputfile', required=True, type=str, help='files in data/[--inputfile]/decimal/* will be read. (only the files named \'cirasame0xx_hogehoge\' will be available)')
parser.add_argument('--outputfiledir', required=True, help='the output file will be saved in :  /data_formated/[--outputfiledir]/cirasame0xx_[--asic].dat')
parser.add_argument('--asic', required=False, type=int, default=0, help='asic No 1~4 ')
args = parser.parse_args()

DIR_PATH = '../data/{}/decimal'.format(args.inputfile)
file_list = glob.glob(os.path.join(DIR_PATH, "*.txt"))
file_list = sorted(file_list, key=lambda s :int(re.search(r'\d+',os.path.basename(s)).group()))


if args.asic == 1:
    range_i = range(0,32)
elif args.asic == 2:
    range_i = range(32,64)
elif args.asic == 3:
    range_i = range(64,96)
elif args.asic == 4:
    range_i = range(96,128)
else:
    range_i = range(128)

col_name = ['DAC_value']
for i in range_i:
    col_name.append('ch{}'.format(i))
out_df = pd.DataFrame(columns=col_name)

for f in file_list:
    df = pd.read_csv(f, sep='\s+', header=None)
    df.columns = ['address', 'row0', 'row1', 'row2', 'row3']
    df = df.drop('address', axis=1)
    #print(df)

    dac = int(re.search(r'\d+',os.path.basename(f)).group())
   
    l = {'DAC_value':dac}
    t = df.iat[0,2]*0.524*0.001

    if t == 0:
        continue 

    for i in range_i:
        readrow = int((i+10)/4)
        readcol = int((i+10)%4)
        l['ch{}'.format(i)]=[df.iat[readrow,readcol]]

    
    l=pd.DataFrame(l) 
    out_df = pd.concat([out_df,pd.DataFrame(l)], ignore_index=True)

s = str(args.inputfile)   
s1= re.split('[/]',s)
filename_sep = re.split('[_.]',s1[1])
output_path = '../data_formated/{}/{}_{:0>2}.dat'.format(args.outputfiledir, filename_sep[0], args.asic)

if not os.path.exists('../data_formated/{}'.format(args.outputfiledir)):
    os.makedirs('../data_formated/{}'.format(args.outputfiledir))

if args.asic == 0:
    out_df.to_csv('{}.dat'.format(args.inputfile), sep=' ', header=None, index=None)
else:
    out_df.to_csv(output_path, sep=' ', header=None, index=None)
