#!/usr/bin/env python3
import numpy as np
import pandas as pd

class OutFileReader:
    def __init__(self, outfilepath_ch:str) -> None:
        self.outfile_ch = pd.read_csv(outfilepath_ch, sep='\s+', header=None)
        colname_ch = ['Global Channel', 'CIRASAME ID', 'ASIC No', 'Channel No', 'Gain DAC', 'Transition Edge 2pe3pe', 'Threshold 0.5pe']
        self.outfile_ch.columns = colname_ch

    def get_outfile_ch(self) -> pd.DataFrame: 
        return self.outfile_ch