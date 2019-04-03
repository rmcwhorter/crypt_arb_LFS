import pandas as pd 
import arrow as ar
import numpy as np
import websocket as ws
import json
import zlib
import time
import threading

import os

import huobi as hu

exchanges = {
    'huobi' : hu
    }

securities = {
    'huobi' : ['ltcusdt','btcusdt','ltcbtc', 'ethusdt', 'ethbtc', 'xlmbtc', 'xlmeth']
}

class tracker:
    def __init__(self, exchange, security, doprint=False):
        if exchange in list(exchanges.keys()):
            self.exchange = exchange
            self.library = exchanges[exchange]
            if security in securities[self.exchange]:
                self.ticker = security
            else:
                print("Invalid security provided")
        else:
            print("Invalid Exchange Provided")

        self.doprint = doprint
        self.data = pd.DataFrame(columns = ['id', 'open', 'close', 'low', 'high', 'amount', 'vol', 'count'])
        #self.begin_tracking()

    
    def begin_tracking(self):
        self.flag = True
        self.sock = ws.WebSocket()
        self.sock.connect(self.library.base_url)    
        self.begin_request = {
            "sub": "market." + self.ticker + ".kline.1min",
            "id": "id1"
            }
            
        self.sock.send(json.dumps(self.begin_request))
        t1 = threading.Thread(target=thread_tracker, args=(self,))
        t1.start()
        
    
    
    def end_tracking(self):
        self.flag = False
        t99 = threading.Thread(target=thread_terminator, args=(self,))
        t99.start()

def decode(data):
    return json.loads(zlib.decompress(data, 16+zlib.MAX_WBITS).decode('utf8'))

def pong(socket):
    request = {'pong' : 128973641298734}
    socket.send(json.dumps(request))

def parse_subscription(data):
    return pd.DataFrame.from_dict(data['tick'], orient='index', columns = ['Values'])

def thread_terminator(self):
    time.sleep(5)
    self.sock.close()

def thread_tracker(self):
    while True and self.flag:
        result = decode(self.sock.recv())
    
        if('status' in list(result.keys())):
            if(result['status'] == 'ok'):
                pass
            elif(result['status'] == 'error'):
                print(result)
        elif('ch' in list(result.keys())):
            result['tick']

            #.format("YYYY-MM-DD HH:mm:ss SSSS ZZ")
            self.data.loc[ar.utcnow().span('microsecond')[0].to("US/Central")] = [
                    result['tick']['id'],
                    result['tick']['open'],
                    result['tick']['close'],
                    result['tick']['low'],
                    result['tick']['high'],
                    result['tick']['amount'],
                    result['tick']['vol'],
                    result['tick']['count']
                ]
                
            if(self.doprint): 
                os.system('cls' if os.name == 'nt' else 'clear')
                print(self.data)

        else:
            pong(self.sock)