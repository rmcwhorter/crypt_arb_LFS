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

base_url = 'data/'
extension = '.pkl'


with open(base_url + "master_pandas" + extension, 'rb') as handle: orders_df = pickle.load(handle)

orders_as_pandas = pd.DataFrame(columns = orders_df['order'][1552331989252].index)

for order in orders_df:
    for timestamp in orders_df[order]:
        print(orders_df[order][1552331924839]['Value']['amount'])
        
        data = {'amount' : orders_df[order][timestamp]['Value']['amount'],
                'ts' : orders_df[order][timestamp]['Value']['ts'],
                'id' : orders_df[order][timestamp]['Value']['id'],
                'price' : orders_df[order][timestamp]['Value']['price'],
                'direction' : orders_df[order][timestamp]['Value']['direction']}
        
        
        tmp_frame = pd.DataFrame(data,columns = orders_df['order'][1552331989252].index)
        
        orders_as_pandas = orders_as_pandas + tmp_frame

print(orders_as_pandas)

print("EOF")