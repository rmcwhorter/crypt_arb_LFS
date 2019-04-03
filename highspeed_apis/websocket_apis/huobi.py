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

base_url = 'wss://api.huobi.pro/hbus/ws'

def subscribe_to_ticker(ticker_pair = 'ethusdt', interval = '1min'):
    ws = websocket.WebSocket()
    ws.connect(base_url)
    
    request = {
            "sub": "market." + ticker_pair + ".kline." + interval,
            "id": "id1"
            }
    
    ws.send(json.dumps(request))
    
    return ws

def pong(socket):
    request = {'pong' : 128973641298734}
    socket.send(json.dumps(request))


def decode(data):
    return json.loads(zlib.decompress(data, 16+zlib.MAX_WBITS).decode('utf8'))

def parse_subscription(data):
    return pd.DataFrame.from_dict(data['tick'], orient='index', columns = ['Values'])

socket = subscribe_to_ticker()
socket.recv()

while True:
    
    result = decode(socket.recv())
    
    if('status' in list(result.keys())):
        if(result['status'] == 'ok'):
            pass
        elif(result['status'] == 'error'):
            print(result)
    elif('ch' in list(result.keys())):
        print(parse_subscription(result))
    else:
        pong(socket)
