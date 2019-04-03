print("SOF")
import time as t
import numpy as np
import pandas as pd
from interruptingcow import timeout as to
import threading
import websocket
import json
import zlib
import time
import pickle
from os import listdir
from os.path import isfile, join
import matplotlib as mpl


base_url = 'k_data/'
extension = '.pkl'

with open("rates_new" + str(1.75) +'.pkl', 'rb') as handle: rates = pickle.load(handle)
with open("rates_correlate_new" + str(1.75) +'.pkl', 'rb') as handle: rates_pred = pickle.load(handle)

base_url = 'monte_carlo_data/'
subset = "_MASSIVE_"

currencies = ['ltcusdt','btcusdt','ltcbtc']  #['btcusdt','ethusdt','ethbtc']
extension = '.pkl'

data_dict = {}

for a in currencies:
    with open(base_url + a + subset + extension, 'rb') as handle: data_dict[a] = pickle.load(handle)

#intersection = data_dict['ltcbtc'].index.intersection(data_dict['btcusdt'].index.intersection(data_dict['ltcusdt'].index)).values
intersection = np.intersect1d(data_dict['ltcusdt'].index.values, np.intersect1d(data_dict['btcusdt'].index.values, data_dict['ltcbtc'].index.values))

def not_in(a,b):
    out = []
    for z in a:
        if(z not in b):
            out.append(z)
    return out

#Min timestamp is 1551423660
#Max timestamp is 1552542540

min_t = 1551423660
max_t = 1552542540

master_idx = []
for a in range(min_t, max_t+60):
    if(a % 60 == 0): master_idx.append(a)

print(len(master_idx))

for currency in currencies:
    df = pd.DataFrame(index=master_idx, columns=data_dict[currency].columns)
    for index in data_dict[currency].index:
        local_data = data_dict[currency].loc[index]
        for data in local_data.index:
            df[index, data] = local_data[data]
    #print(df)

'''
print(ltcusdt)
print(btcusdt)
print(ltcbtc)'''

k_values = data_dict['ltcusdt']['close']/data_dict['btcusdt']['close'] - data_dict['ltcbtc']['close']

mu = np.mean(k_values)
sigma = np.std(k_values)

z_scores = (k_values - mu) / sigma

pd.options.display.max_rows = 10
df = pd.DataFrame(rates, index=rates_pred, columns=["% Correct"])
#print(df.sort_values("% Correct", ascending=False))
#39 prediciting 39 is the highest value

#print(ltcusdt)
#print(btcusdt)
#print(ltcbtc)

#df_timeseries = pd.DataFrame([data_dict['ltcusdt']['close']/data_dict['btcusdt']['close'], data_dict['ltcbtc']['close'], k_values, z_scores], index=data_dict['ltcbtc'].index, columns=["LTCUSDT / BTCUSDT", "LTC/BTC", "K_VALUE", "Z_SCORE"])

'''
print(data_dict['ltcusdt']['close']/data_dict['btcusdt']['close'])
print(data_dict['ltcbtc']['close'])'''


print("EOF")