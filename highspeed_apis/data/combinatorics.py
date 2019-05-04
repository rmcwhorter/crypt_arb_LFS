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
import requests

url = 'https://api.huobi.com/v1/common/symbols'
data = requests.get(url=url).json()['data']

inv_data = []
for a in data:
    tmp_a = a['base-currency'][:]
    tmp_b = a['quote-currency'][:]
    total = dict(a)
    total['quote-currency'] = tmp_a
    total['base-currency'] = tmp_b
    inv_data.append(total)

def combine(length, base, quote):
    out = []
    for tick in data:
        if(tick['base-currency'] == base and tick['quote-currency'] == quote):
            out.append(str(tick['base-currency']+"/"+tick['quote-currency']))
        elif(length > 1 and tick['base-currency'] == base):
            d = combine(length-1, tick['quote-currency'], quote)
            if(len(d) > 0):
                out.append(tick['base-currency']+"/"+tick['quote-currency']+"/"+str(d[0]))

    return out

for tick in data+inv_data:
    c = combine(10, tick['base-currency'], tick['quote-currency'])
    print()
    print(tick['base-currency'], " ", tick['quote-currency'])
    print(c)
    print(len(c))

print("EOF")