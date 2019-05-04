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
import currency_pairs
import arrow
import os

currencies = currency_pairs.currency_pairs

'''
base_url = 'wss://api2.poloniex.com'
ws = websocket.WebSocket()
ws.connect(base_url)

formatted_request = {"command": "subscribe", "channel": 1002}
ws.send(json.dumps(formatted_request))

responses = []
start = time.time()
while True and time.time() < start + 15:
    responses.append([arrow.utcnow().to('US/Central'), json.loads(ws.recv())])

ws.close()

with open("data/15_second_responses.pkl", 'wb') as handle: pickle.dump(responses, handle, protocol=pickle.HIGHEST_PROTOCOL)
'''

start = time.time()
with open("data/15_second_responses.pkl", 'rb') as handle: responses = pickle.load(handle)
end = time.time()

print(f"We loaded {os.path.getsize('data/15_second_responses.pkl')} bytes in {end-start} seconds ({os.path.getsize('data/15_second_responses.pkl')/(end-start)} bytes/second)\n")

print(f"Initial Contact: {responses[0]}\n")
'''
for data in responses[1:]:
    print(data)'''

new_data = []
for data in responses[1:]:
    tmp = [data[0], data[1][0], data[1][1], *data[1][2]]
    new_data.append(tmp)

master_df = pd.DataFrame(new_data, columns=['timestamp', 'code','none', 'currency_pair', 'last_price', 'lowest_ask', 'highest_bid', '24_hr_change_pct', '24_hr_base_volume', '24_hr_quote_volume', 'is_frozen', '24_hr_high', '24_hr_low']).drop(columns=['none']).set_index('timestamp')

tmp = [None]*len(master_df)
master_df['currency_pair_literal'] = master_df['current_spread'] = master_df['24_hr_spread'] = tmp

for index, row in master_df.iterrows():
    try:
        master_df.loc[index, 'currency_pair_literal'] = currency_pairs.inv_currency_pairs[row['currency_pair']]
    except:
        master_df.loc[index, 'currency_pair_literal'] = -1
    else:
        pass
    
    try:
        master_df.loc[index, 'current_spread'] = np.float64(row['highest_bid']) - np.float64(row['lowest_ask'])
    except:
        master_df.loc[index, 'current_spread'] = np.nan
        print(row['highest_bid'], type(row['highest_bid']))
    else:
        pass #print(row['highest_bid'], type(row['highest_bid']))

    try:
        master_df.loc[index, '24_hr_spread'] = np.float64(row['24_hr_high']) - np.float64(row['24_hr_low'])
    except:
        master_df.loc[index, '24_hr_spread'] = np.nan
    else:
        pass

print(master_df)

with open("data/summary_ledger.pkl", "wb") as handle: pickle.dumps(master_df, protocol=pickle.HIGHEST_PROTOCOL)

print(master_df.columns.values)

print("EOF")