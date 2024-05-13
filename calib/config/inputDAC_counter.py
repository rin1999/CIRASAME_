"""
run this code to check if there are 32 channels in inputDAC.yml
"""

import yaml
import argparse

def counter(data:dict, citiroc:str) -> int:
    l = data[citiroc]['Input 8-bit DAC']
    return len(l)

parser = argparse.ArgumentParser()
parser.add_argument('-n','--name', default='')
args = parser.parse_args()

file_dir = args.name + '/InputDAC.yml'
citiroc_list = ['CITIROC1','CITIROC2','CITIROC3','CITIROC4']

with open(file_dir,'r') as file:
    data = yaml.safe_load(file)
    for s in citiroc_list:
        if counter(data,s) != 32 :
            print('ERROR!: There are '+str(counter(data,s))+' channels in '+s)
    
