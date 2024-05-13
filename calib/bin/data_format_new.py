#!/usr/bin/env python3
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


def process_data(run_name, iCIRASAME, iASIC):

    if iASIC == 1:
        range_i = range(0, 32)
    elif iASIC == 2:
        range_i = range(32, 64)
    elif iASIC == 3:
        range_i = range(64, 96)
    elif iASIC == 4:
        range_i = range(96, 128)
    else:
        range_i = range(128)

    dir_name = f"/home/nestdaq/cirasame/calib/data/{run_name}/cirasame{iCIRASAME:03}/decimal"
    files = os.listdir(dir_name)
    files_with_extension = [file for file in files if file.endswith(f".txt")]
    dat_files = sorted(files_with_extension)
    print(f"dir_name {dir_name}")
    print(f"dat_files {dat_files}")

    col_name = ['DAC_value']
    for i in range_i:
        col_name.append(f"ch{i}")
        out_df = pd.DataFrame(columns=col_name)
        
    for f in dat_files:
        print(f)
        df = pd.read_csv(f"{dir_name}/{f}", sep='\s+', header=None)
        df.columns = ['address', 'row0', 'row1', 'row2', 'row3']
        df = df.drop('address', axis=1)
        dac = int(re.search(r'\d+', os.path.basename(f)).group())
        l = {'DAC_value':dac}
        t = df.iat[0,2]*0.524*0.001
        
        if t == 0:
            continue 
            
        for i in range_i:
            readrow = int((i+10)/4)
            readcol = int((i+10)%4)
            l[f"ch{i}"] = [df.iat[readrow, readcol]]
                
        l = pd.DataFrame(l) 
        out_df = pd.concat([out_df, pd.DataFrame(l)], ignore_index=True)
            
    output_basedir = "/home/nestdaq/cirasame/calib/data_formated"
    output_rundir = f"{output_basedir}/thresholdscan_{run_name}"
    output_filename = f"{output_rundir}/cirasame{iCIRASAME:03}_{iASIC:0>2}.dat"
        
    if not os.path.exists(output_rundir):
        print(f"{output_rundir} not found")
        os.makedirs(f"{output_rundir}"
        
    if args.asic == 0:
#        out_df.to_csv("{args.inputfile}.dat", sep=' ', header=None, index=None)
        print(f"cirasame_{run_name}.dat")
    else:
#        out_df.to_csv(output_path, sep=' ', header=None, index=None)
        print(f"{output_filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--run_name", required=True, type=str, help='scan run name e.g. 20240422_2200')
    args = parser.parse_args()
    
    for iCIRASAME in range(1, 2):
        for iASIC in range(1, 2):
            process_data(args.run_name, iCIRASAME, iASIC)

if __name__ == "__main__":
    main()
