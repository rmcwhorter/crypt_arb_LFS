print("SOF")
import currency_pairs
import pandas as pd 
import numpy as np 
import websocket
import json
import time
import arrow
import threading
import pickle
import os

#Arrow Time => message data
data_dict = {}

base_url = 'wss://api2.poloniex.com'

ws = websocket.WebSocket()
ws.connect(base_url)

formatted_request = {"command": "subscribe", "channel": 1002}
ws.send(json.dumps(formatted_request))

start = time.time()
end = start + 60*60*15

def writer():
    global data_dict
    global ws
    count = 0
    while time.time() < end:
        time.sleep(15)
        print(f"\nOn the {count} iteration.")
        print(f"Connection: {ws.connected}")
        tmp = data_dict.copy()
        data_dict = {}
        out_str = f"data/overnight_raw/{time.time()}.pkl"
        if bool(tmp):
            try:
                print("Writing")
                with open(out_str, 'wb') as handle: pickle.dump(tmp, handle, protocol=pickle.HIGHEST_PROTOCOL)
            except:
                print(f"\n***** CATESTROPHIC FAILURE *****\nUNABLE TO WRITE TO FILE. DATA BACKED UP FOR NEW RUN. ENSURE THREAD IS STILL ALIVE.")
                data_dict = data_dict.update(tmp)
            else:
                del tmp
                print("Written")
        else:
            #dict is empty
            print(tmp)
        count += 1
    

writer = threading.Thread(target=writer)
writer.start()

def is_alive():
    global writer
    while True and time.time() < end:
        time.sleep(0.5)
        if not writer.is_alive():
            os.system('afplay /System/Library/Sounds/Ping.aiff')
            print(f"===== CATESTROPHIC FAILURE =====\nWRITING THREAD IS NO LONGER ALIVE")

threading.Thread(target=is_alive).start()

while True and time.time() < end:
    msg = json.loads(ws.recv())
    if(msg[0] == 1010):
        #We just recieved a heartbeat, the server is checking up on us to make sure we know its still there.
        print("Heartbeat") 
    elif(msg[0] == 1002):
        if(msg[1] == 1):
            #we just recieved our initial message.
            print("Initilized")
        else:
            data_dict[arrow.now()] = msg[2]
            #print("Tick")

    else:
        pass

ws.close()

'''
import os

directory = os.fsencode("data/overnight_raw/")

for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".asm") or filename.endswith(".py"): 
         # print(os.path.join(directory, filename))
         continue
     else:
         continue'''

print("EOF")