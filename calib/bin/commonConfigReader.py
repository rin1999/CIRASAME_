#!/usr/bin/env python3

"""
Class for reading common config files written under config dir.
"""

import yaml
PATH = "/data/e50test_202404/cirasame/CIRASAME_calib/config"
#PATH = "~/cirasame/calib/config"
IP_MAP = "ipmap.yml"
THRESHOLDSCAN_RANGE = "thresholdscan_range.yml"
COMMON_PATH = "commonpath.yml"

class CommonConfigReader :

    def __init__(self):
        with open(f"{PATH}/{IP_MAP}", "r") as f :
            self.ip_map = yaml.safe_load(f)
        with open(f"{PATH}/{THRESHOLDSCAN_RANGE}", "r") as f :
            self.thresholdscan_range = yaml.safe_load(f)
        with open(f"{PATH}/{COMMON_PATH}", "r") as f :
            self.common_path = yaml.safe_load(f)

    def readAllCirasameIP(self) -> dict:
        ip_dict = self.ip_map["cirasameIP"]
        return ip_dict

    def readCirasameIP(self, cirasame_num :int) -> str:
        ip_address = self.ip_map["cirasameIP"][cirasame_num]
        return ip_address
    
    def readThresholdScanRange(self) -> dict:
        thres_range = self.thresholdscan_range
        return thres_range
    
    def readCommonPath(self) -> dict:
        path_dict = self.common_path
        return path_dict