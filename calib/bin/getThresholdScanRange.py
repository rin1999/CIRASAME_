#!/usr/bin/env python3
import commonConfigReader

config = commonConfigReader.CommonConfigReader()
range_dict = config.readThresholdScanRange()


range_list = []
range_list.append(range_dict["start"])
range_list.append(range_dict["end"])
range_list.append(range_dict["step"])


print(f"[start, end, step] = {range_list}")