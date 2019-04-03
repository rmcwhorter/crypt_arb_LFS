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

print(from_time < current_time)

trial_results = []

'''
We're going to say that the defination of a trade's results is the percent difference between the closing value at the point it was executed and the closing value one time unit's in the future
i.e. a trade made on 30 minutes of data is evaluated 30 minutes in the future.
'''

currencies = ['btcusdt','ethusdt','ethbtc']

request = {"req": "market.ethusdt.kline.1min","id": "id10", "from": 1552331924, "to": 1552334326}

base_url = 'wss://api.huobi.pro/hbus/ws'
ws = websocket.WebSocket()
ws.connect(base_url)

responses = []

for a in currencies:
    formatted_request = {"req": str("market."+a+".kline.1min"),"id": "id10", "from": from_time}
    ws.send(json.dumps(formatted_request))
    tmp_response = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS).decode('utf8'))
    if('status' in tmp_response.keys()):
        if(tmp_response['status'] == 'ok'):
            print(tmp_response['data'])
            responses.append(tmp_response['data'])
        else:
            print(tmp_response)

ws.close()


frames = []

for a in responses:
    tmp = pd.DataFrame(columns = ['open','close','low','high','amount','vol','count'])
    for b in a:
        tmp = tmp.append(pd.DataFrame(b, index=[b['id']]).drop('id', axis=1))
    frames.append(tmp)



for a in range(len(frames)):
    with open(str('monte_carlo_data/'+ currencies[a] +'.pkl'), 'wb') as handle: pickle.dump(frames[a], handle, protocol=pickle.HIGHEST_PROTOCOL)

print("EOF")