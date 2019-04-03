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

chart_file = 'data/master_chart.pkl'
orders_file = 'data/master_orders.pkl'

with open(chart_file, 'rb') as handle: chart_df = pickle.load(handle)
with open(orders_file, 'rb') as handle: orders_df = pickle.load(handle)

print(orders_df)
print(chart_df)

#open_arr.append(a.loc['open'][0])
#dtype = dict(names = ['ts',''], formats=formats)
print(np.array(list(orders_df.items())).shape)
#print(orders_df.loc[''])

#data = {'amount','price','direction'}