"""
read out the values from CIRASAME

2024.01.26 R.Okazaki
"""

import os
import sys
import time
import yaml
import argparse
import subprocess as sub
import numpy as np
#import shutil
#import PySimpleGUI as sg

measurement_time = 1.0


#args -> --name (default is "data_default"), --settings
#getting arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n','--name', default='data_default')
#parser.add_argument('-ip', '--ip_address', default='192.168.10.16')
parser.add_argument('-s','--settings', default='yaml_files/settings.yml')
args = parser.parse_args()

SETTING_FILE_PATH = args.settings

#if args.settings == None:
#    print('error: No argument for --settings')
#    sys.exit()

#CIRASAME_IP = args.ip_address
#print(CIRASAME_IP)

#generating data directry
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('data/'+args.name):
    os.makedirs('data/'+args.name)
if not os.path.exists('data/'+args.name+'/binary'):
    os.makedirs('data/'+args.name+'/binary')
if not os.path.exists('data/'+args.name+'/decimal'):
    os.makedirs('data/'+args.name+'/decimal')

#loading settings (save your default settings at "yaml_files/settings.yaml")
with open(SETTING_FILE_PATH, encoding='utf-8') as f:
    settings = yaml.safe_load(f)

CITIROC_PATH = settings['CITIROC_path']
HUL_PATH     = settings['HUL_path']
YAML_PATH    = settings['YAML_path']
CIRASAME_IP  = settings['CIRASAME_ip']
DAC_SCAN     = settings['DAC_scan']


scan_dac_value = []

for i in range(int(DAC_SCAN['steps'])):
    scan_dac_value.append(int(DAC_SCAN['start'])+i*int(DAC_SCAN['gap']))

#setting progress bar
"""
sg.theme('Dark Red')
PROGRESS_MAX = len(scan_dac_value)
current_progress = 0
layout = [[sg.Text('taking data...')],
          [sg.ProgressBar(PROGRESS_MAX, orientation='h', size=(20,20), key='-PROG-')],
          [sg.Cancel()]]
window = sg.Window('scaler reader', layout)
"""
#sub.run([CITIROC_PATH+'/femcitiroc_control', '-ip='+CIRASAME_IP, '-yaml='+YAML_PATH+'/InputDAC.yml', '-sc', '-read', '-q'])

t_start = time.time()

with open(YAML_PATH+'/RegisterValue.yml', 'r') as f:
    savefile = yaml.safe_load(f)

#main part of reading scaler
for dac in scan_dac_value:
    
    with open(YAML_PATH+'/RegisterValue.yml', 'r') as f:
        yml_RegVal = yaml.safe_load(f)
    print('start : DAC2 = {}'.format(str(dac)))
    yml_RegVal['CITIROC1']['DAC2 code'] = dac
    yml_RegVal['CITIROC2']['DAC2 code'] = dac
    yml_RegVal['CITIROC3']['DAC2 code'] = dac
    yml_RegVal['CITIROC4']['DAC2 code'] = dac
    with open(YAML_PATH+'/RegisterValue.yml', 'w') as f:
        yaml.dump(yml_RegVal, f)
    
    """
    event, values = window.read(timeout=10)
    if event == 'Cancel' or event == sg.WIN_CLOSED:
        break
    window['-PROG-'].update(current_progress)
    current_progress = current_progress+1
    """

    sub.run([CITIROC_PATH+'/femcitiroc_control', '-ip='+CIRASAME_IP, '-yaml='+YAML_PATH+'/RegisterValue.yml', '-yaml='+YAML_PATH+'/InputDAC.yml', '-yaml='+YAML_PATH+'/DiscriMask.yml', '-sc', '-read', '-q'])
    sub.run([HUL_PATH+'/write_register', CIRASAME_IP, '0x80000000', '0x1', '1'])
    time.sleep(measurement_time)
    sub.run([HUL_PATH+'/read_scr', CIRASAME_IP, 'data/'+args.name+'/binary/dataBin{}.dat'.format(str(dac))])
    print(yml_RegVal['CITIROC1']['DAC2 code'])
    
t_end = time.time()
with open(YAML_PATH+'/RegisterValue.yml', 'w') as f:
    yaml.dump(savefile, f)

# rewriting binary data to decimal data
for i in scan_dac_value:
    i = int(i)
    #    output_str = sub.run(['od', '-Ad', '-td', '-v', 'data/'+args.name+'/binary/dataBin{}.dat'.format(str(i))], stdout=sub.PIPE, text=True)
    # Run the command and capture stdout as bytes
    output_bytes = sub.run(['od', '-Ad', '-td', '-v', 'data/'+args.name+'/binary/dataBin{}.dat'.format(str(i))], stdout=sub.PIPE).stdout

    # Decode stdout to a string
    output_str = output_bytes.decode('utf-8')  # Assuming UTF-8 encoding, adjust as needed
    #print(output_str)
    with open('data/'+args.name+'/decimal/dataDec{}.txt'.format(str(i)), 'w') as f:
        f.write(output_str)

print(scan_dac_value)

t_elapsed = int(t_end-t_start)
hour = t_elapsed//3600
minute = (t_elapsed%3600)//60
second = (t_elapsed%3600%60)
print("elapsed time")
print(str(hour).zfill(2) + ":" + str(minute).zfill(2) + ":" + str(second).zfill(2))
