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

#1552331924
#1546326000 Jan 1st at 1am
current_time = int(str(time.time())[0:len('1552331924')])-5 #current time minus 5 min
from_time =  1552201200

trial_results = []

'''
We're going to say that the defination of a trade's results is the percent difference between the closing value at the point it was executed and the closing value one time unit's in the future
i.e. a trade made on 30 minutes of data is evaluated 30 minutes in the future.
'''

def dict_val_exists_and_equals(dictionary, value, check):
    if(value in list(dictionary.keys())):
        flag = True
    else:
        flag = False
    
    if(flag):
        if(dictionary[value] == check):
            return True
        else:
            return False
    else:
        return False

subset = "_MASSIVE_THIRD_"

#['qtum/usdt', 'qtum/btc/btc/usdt', 'qtum/eth/eth/btc/btc/usdt']
currencies = ['qtumusdt','qtumbtc','btcusdt', 'qtumeth','ethbtc'] #['ltcusdt','btcusdt','ltcbtc']
#responses = {'ltcusdt' : [],'btcusdt' : [],'ltcbtc' : []} #{'ltcusdt' : [],'btcusdt' : [],'ltcbtc' : []}
responses = {}
for c in currencies:
    responses[str(c)] = []


start_time = 1546326000
end_time = start_time + 150*60

base_url = 'wss://api.huobi.pro/hbus/ws'
ws = websocket.WebSocket()
ws.connect(base_url)



epoch = 240


for a in currencies:
    print(a)
    start_time = 1551423600
    end_time = start_time + 300*60
    for _ in range(epoch):
        formatted_request = {"req": str("market."+a+".kline.1min"),"id": "id10", "from": start_time, "to" : end_time}
        ws.send(json.dumps(formatted_request))
        tmp_response = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS).decode('utf8'))      
        
        while(not dict_val_exists_and_equals(tmp_response, 'status', 'ok')): # and not dict_val_exists_and_equals(tmp_response, 'data', not [])
            ws.send(json.dumps(formatted_request))
            print(tmp_response)
            print("Failed to gather data")
            tmp_response = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS).decode('utf8'))
            time.sleep(1)
        
        print("Successfully Gathered Data")

        #print(tmp_response)
        
        tmp = tmp_response['data']
        responses[a].append(tmp)
        start_time += 300*60
        end_time = start_time + 300*60

ws.close()


frames = []

for a in responses:
    print("Iterating Responses")
    interim = []
    for b in responses[a]:
        tmp = pd.DataFrame(columns = ['open','close','low','high','amount','vol','count'])
        for c in b:
            tmp = tmp.append(pd.DataFrame(c, index=[c['id']]).drop('id', axis=1))
        interim.append(tmp)
        
    tmp = pd.DataFrame(columns = ['open','close','low','high','amount','vol','count'])
    for b in interim:
        tmp = tmp.append(b)
    frames.append(tmp)

for a in frames:
    print("Iterating Frames")
    for column in a:
        sub_index = a.index.values
        for index in range(len(sub_index)):
            if(type(a[column][sub_index[index]]) not in [np.float64, int]):
                if(type(a[column][sub_index[index]]) == pd.core.series.Series):
                    a[column][sub_index[index]] = a[column][sub_index[index]].values[0]


for a in range(len(frames)):
    with open(str('monte_carlo_data/'+ currencies[a] + subset +'.pkl'), 'wb') as handle: pickle.dump(frames[a], handle, protocol=pickle.HIGHEST_PROTOCOL)

print("EOF")