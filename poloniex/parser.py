print("SOF")
import currency_pairs
import pandas as pd 
import numpy as np 
import websocket
import json
import time
import arrow
import threading
import pickle

import os

path = "data/overnight_raw/"
directory = os.fsencode(path)

data_dict = {}

for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".pkl") or filename.endswith(".py"): 
        with open(path + filename, "rb") as handle: tmp = pickle.load(handle)
        for a in tmp:
            data_dict[a] = tmp[a]
     else:
         continue

frame = pd.DataFrame.from_dict(data_dict).transpose()
#[ <currency pair id>, "<last trade price>", "<lowest ask>", "<highest bid>", "<percent change in last 24 hours>", "<base currency volume in last 24 hours>", "<quote currency volume in last 24 hours>", <is frozen>, "<highest trade price in last 24 hours>", "<lowest trade price in last 24 hours>" ], 
frame.columns = ["currency_pair_id", "last_trade_price", "lowest_ask", "highest_bid", "pct_change_24_hr", "base_volume_24_hr", "quote_volume_24_hr", "is_frozen", "24_hr_high", "24_hr_low"]
print(frame.head)
print(frame.columns)

with open("data/data_parsed/parsed.pkl", "wb") as handle: pickle.dump(frame, handle, pickle.HIGHEST_PROTOCOL)

print("EOF")