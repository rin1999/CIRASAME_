import subprocess
import os 
import argparse

IP_LIST = ['192.168.2.101','192.168.2.102','192.168.2.103',
           '192.168.2.104','192.168.2.105','192.168.2.106',
           '192.168.2.107','192.168.2.108','192.168.2.109',
           '192.168.2.110','192.168.2.111','192.168.2.112',
           '192.168.2.113','192.168.2.114','192.168.2.115',
           '192.168.2.116','192.168.2.117','192.168.2.118']

CMD = os.path.expanduser('~/cirasame/CitirocControlSoft/bin/femcitiroc_control')
YAML= os.path.expanduser('~/cirasame/calib/config')
OTHER='-sc -read'


def main():
    process_list = []
    for i in range(18):
        ip = IP_LIST[i]
        args = [CMD, f'-ip={ip}', f'-yaml={YAML}/cirasame{i:03}/DiscriMask.yml', f'-yaml={YAML}/cirasame{i:03}/RegisterValue.yml', f'-yaml={YAML}/cirasame{i:03}/InputDAC.yml', OTHER]
        print(f'Start : cirasame{i:03}')
        process_list.append(subprocess.Popen(args))
    for p in process_list:
        p.communicate()

if __name__ == '__main__':
    main()