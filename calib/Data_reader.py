import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import re
import glob
import numpy as np


class Data_reader:

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        file_list = glob.glob(os.path.join(self.file_path,'*.txt'))
        self.hits = []
        self.dac_val = []
        

        