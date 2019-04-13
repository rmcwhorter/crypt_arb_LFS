import pandas as pd
import numpy as np 
import pickle as pk
import arrow as ar

base_url = 'data/raw/'
subset = "_MASSIVE_THIRD_"

currencies = ['btcusdt', 'ethbtc', 'qtumbtc', 'qtumeth', 'qtumusdt']
extension = '.pkl'

data_dict = {}

for a in currencies:
    with open(base_url + a + subset + extension, 'rb') as handle: data_dict[a] = pk.load(handle)

min_max_times = []
max_min_times = []

for a in data_dict:
    min_max_times.append(data_dict[a].index.values[-1])
    max_min_times.append(data_dict[a].index.values[0])

min_time = max(max_min_times)
max_time = min(min_max_times)

for a in data_dict:
    s = data_dict[a].index.values
    indices_a = s > min_time
    indices_b = s < max_time
    indices_to_drop = []
    truth_indices = indices_a * indices_b
    
    for index in range(len(s)):
        if(not truth_indices[index]): indices_to_drop.append(s[index])
    
    data_dict[a].drop(indices_to_drop, inplace=True)

for a in data_dict:
    print(data_dict[a])

#set the ethereal set of indices, one minute from min to max
real_ts = []
for a in range(int((max_time-min_time)/60)):
    real_ts.append(int(min_time + 60))

print(len(real_ts))

for a in data_dict:
    for b in range(len(data_dict[a].index.values)-1):
        if(data_dict[a].index.values[b + 1] - data_dict[a].index.values[b] != 60):
            print(data_dict[a].index.values[b + 1] - data_dict[a].index.values[b])


print("EOF")