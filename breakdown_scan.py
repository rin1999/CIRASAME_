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

parser = argparse.ArgumentParser()
parser.add_argument('-n','--name', default='data_default')
parser.add_argument('-s','--settings', default='yaml_files/settings.yml')
parser.add_argument('--scan', required=True, type=int, nargs="*", help='set range of biasDAC scan. 3 inputs required.\n --scan <start DAC> <diff between each step> <number of steps>')
args = parser.parse_args()

SETTING_FILE_PATH = args.settings

# check length of --scan arg list
if len(args.scan) != 3:
    print('Error : 3 args required. You entered {} values.'.format(len(args.scan)))
    sys.exit()

#scandac_list = np.arange(args.scan[0], args.scan[0]-args.scan[1]*args.scan[2], args.scan[2])
scandac_list = args.scan[0] - np.arange(args.scan[2])*args.scan[1]

print('scan start DAC : {}'.format(args.scan[0]))
print('scan end DAC : {}'.format(args.scan[0] - args.scan[1]*args.scan[2]))
print('scan range : {}'.format(scandac_list))

#generating data directry

DATA_DIR_BASE='data/biasscan'

if not os.path.exists(DATA_DIR_BASE):
    print("No data directory found. Exitting.")
    exit
if not os.path.exists(DATA_DIR_BASE+'/'+args.name):
    os.makedirs(DATA_DIR_BASE+'/'+args.name)
if not os.path.exists(DATA_DIR_BASE+'/'+args.name+'/binary'):
    os.makedirs(DATA_DIR_BASE+'/'+args.name+'/binary')
if not os.path.exists(DATA_DIR_BASE+'/'+args.name+'/decimal'):
    os.makedirs(DATA_DIR_BASE+'/'+args.name+'/decimal')


#loading settings (save your default settings at "yaml_files/settings.yaml")
with open(SETTING_FILE_PATH, encoding='utf-8') as f:
    settings = yaml.safe_load(f)

CITIROC_PATH = settings['CITIROC_path']
HUL_PATH     = settings['HUL_path']
YAML_PATH    = settings['YAML_path']
CIRASAME_IP  = settings['CIRASAME_ip']
#DAC_SCAN     = settings['DAC_scan']

# define commands
set_max1932 = HUL_PATH + '/set_max1932'




#for i in range(int(DAC_SCAN['steps'])):
#    scan_dac_value.append(int(DAC_SCAN['start'])+i*int(DAC_SCAN['gap']))

#sub.run([CITIROC_PATH+'/femcitiroc_control', '-ip='+CIRASAME_IP, '-yaml='+YAML_PATH+'/InputDAC.yml', '-sc', '-read', '-q'])

t_start = time.time()

#with open(YAML_PATH+'/RegisterValue.yml', 'r') as f:
#    savefile = yaml.safe_load(f)

#main part of reading scaler


print([CITIROC_PATH+'/femcitiroc_control', '-ip='+CIRASAME_IP, '-yaml='+YAML_PATH+'/RegisterValue.yml', '-yaml='+YAML_PATH+'/InputDAC.yml', '-yaml='+YAML_PATH+'/DiscriMask.yml', '-sc', '-read', '-q'])
sub.run([CITIROC_PATH+'/femcitiroc_control', '-ip='+CIRASAME_IP, '-yaml='+YAML_PATH+'/RegisterValue.yml', '-yaml='+YAML_PATH+'/InputDAC.yml', '-yaml='+YAML_PATH+'/DiscriMask.yml', '-sc', '-read', '-q'])

for bias in scandac_list:
    print('bias {} scan'.format(bias))
    print([set_max1932, CIRASAME_IP, str(bias)])
    sub.run([set_max1932, CIRASAME_IP, str(bias)])
    print([HUL_PATH+'/write_register', CIRASAME_IP, '0x80000000', '0x1', '1'])
    sub.run([HUL_PATH+'/write_register', CIRASAME_IP, '0x80000000', '0x1', '1'])
    time.sleep(1)
    print([HUL_PATH+'/read_scr', CIRASAME_IP, DATA_DIR_BASE+'/'+args.name+'/binary/dataBin{}.dat'.format(str(bias))])
    sub.run([HUL_PATH+'/read_scr', CIRASAME_IP, DATA_DIR_BASE+'/'+args.name+'/binary/dataBin{}.dat'.format(str(bias))])


for bias in scandac_list:
    output_bytes = sub.run(['od', '-Ad', '-td', '-v', DATA_DIR_BASE+'/'+args.name+'/binary/dataBin{}.dat'.format(str(bias))], stdout=sub.PIPE).stdout
    output_str = output_bytes.decode('utf-8')
    with open(DATA_DIR_BASE+'/'+args.name+'/decimal/dataDec{}.txt'.format(str(bias)), 'w') as f:
        f.write(output_str)



"""
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
    

    sub.run([CITIROC_PATH+'/femcitiroc_control', '-ip='+CIRASAME_IP, '-yaml='+YAML_PATH+'/RegisterValue.yml', '-yaml='+YAML_PATH+'/InputDAC.yml', '-yaml='+YAML_PATH+'/DiscriMask.yml', '-sc', '-read', '-q'])
    sub.run([HUL_PATH+'/write_register', CIRASAME_IP, '0x80000000', '0x1', '1'])
    time.sleep(1)
    sub.run([HUL_PATH+'/read_scr', CIRASAME_IP, 'data/'+args.name+'/binary/dataBin{}.dat'.format(str(dac))])
    print(yml_RegVal['CITIROC1']['DAC2 code'])
"""



t_end = time.time()
"""
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
"""

t_elapsed = int(t_end-t_start)
hour = t_elapsed//3600
minute = (t_elapsed%3600)//60
second = (t_elapsed%3600%60)
print("elapsed time")
print(str(hour).zfill(2) + ":" + str(minute).zfill(2) + ":" + str(second).zfill(2))
