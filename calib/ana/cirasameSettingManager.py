#!/usr/bin/env python3

"""
Reading and re-Writing setting files for each cirasame.
You can edit:
    DiscriMask.yml
    InputDAC.yml
    RegisterValue.yml
"""

import yaml
import os
PATH = "~/cirasame/calib/config"
DISCRI = "DiscriMask.yml"
INPUTDAC = "InputDAC.yml"
REGVAL = "RegisterValue.yml"

class CirasameSettingManager:

    def __init__(self, cirasameID:int) -> None:
        self.cirasameID = cirasameID
        self.PATH_EXPANDED = os.path.expanduser(PATH)
        with open(f"{self.PATH_EXPANDED}/cirasame{cirasameID:03}/{DISCRI}") as f:
            self.discriMask = yaml.safe_load(f)
        with open(f"{self.PATH_EXPANDED}/cirasame{cirasameID:03}/{INPUTDAC}") as f:
            self.inputDAC = yaml.safe_load(f)
        with open(f"{self.PATH_EXPANDED}/cirasame{cirasameID:03}/{REGVAL}") as f:
            self.registerValue = yaml.safe_load(f)

    def readDiscriMask(self) -> dict:
        out_discrimask = self.discriMask
        return out_discrimask
    
    def readInputDAC(self) -> dict:
        out_inputDAC = self.inputDAC
        return out_inputDAC
    
    def readRegisterValue(self) -> dict:
        out_registervalue = self.registerValue
        return out_registervalue
    
    def dumpDiscriMask(self) -> None:
        with open(f"{self.PATH_EXPANDED}/cirasame{self.cirasameID:03}/{DISCRI}", "w") as f:
            yaml.dump(self.discriMask, f)

    def dumpInputDAC(self) -> None:
        with open(f"{self.PATH_EXPANDED}/cirasame{self.cirasameID:03}/{INPUTDAC}", "w") as f:
            yaml.dump(self.inputDAC, f)

    def dumpRegisterValue(self) -> None:
        with open(f"{self.PATH_EXPANDED}/cirasame{self.cirasameID:03}/{REGVAL}", "w") as f:
            yaml.dump(self.registerValue, f)
