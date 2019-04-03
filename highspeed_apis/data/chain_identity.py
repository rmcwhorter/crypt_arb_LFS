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

currencies = ['ltcusdt','btcusdt','ltcbtc']

request = {"req": "market.ethusdt.kline.1min","id": "id10", "from": 1552331924, "to": 1552334326}

base_url = 'wss://api.huobi.pro/hbus/ws'
ws = websocket.WebSocket()
ws.connect(base_url)

responses = []

for a in currencies:
    formatted_request = {"req": str("market."+a+".kline.1min"),"id": "id10", "from": 1552331924, "to": 1552334326}
    ws.send(json.dumps(formatted_request))
    tmp_response = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS).decode('utf8'))
    if('status' in tmp_response.keys()):
        if(tmp_response['status'] == 'ok'):
            responses.append(tmp_response['data'])
        else:
            print(tmp_response)



frames = []

for a in responses:
    tmp = pd.DataFrame(columns = ['open','close','low','high','amount','vol','count'])
    for b in a:
        tmp = tmp.append(pd.DataFrame(b, index=[b['id']]).drop('id', axis=1))
    frames.append(tmp)

print(responses[0] == responses[1])

print(frames)

print(np.sum((frames[0]['close']/frames[1]['close']) - (frames[2]['close'])))


print("EOF")