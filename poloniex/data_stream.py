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

base_url = 'wss://api2.poloniex.com'

data_set = {}

columns = ['code', 'currency_pair', 'last_price', 'lowest_ask', 'highest_bid', '24_hr_change_pct', '24_hr_base_volume', '24_hr_quote_volume', 'is_frozen', '24_hr_high', '24_hr_low', 'currency_pair_literal', 'current_spread', '24_hr_spread', 'timestamp']

for t in currency_pairs.inv_currency_pairs:
    data_set[t] = pd.DataFrame(columns = columns)
    data_set[t] = data_set[t].set_index('timestamp')

raw_ledger = pd.DataFrame(columns = columns)
raw_ledger = raw_ledger.set_index('timestamp')

start = time.time() + 15#60*7

def thread_warning(time_param, bound = 5):
    while True and time.time() < time_param+1:
        if(threading.active_count() > bound):
            print(f"Thread count has exceeded boundary ({threading.active_count()})")

def writing(msg):
    global raw_ledger
    #we want to prepare the data to append to the master ledger
    df = pd.DataFrame([arrow.now(), msg[0], *msg[2]]).T
    df.columns = ['timestamp', 'code', 'currency_pair', 'last_price', 'lowest_ask', 'highest_bid', '24_hr_change_pct', '24_hr_base_volume', '24_hr_quote_volume', 'is_frozen', '24_hr_high', '24_hr_low']
    df['currency_pair_literal'] = currency_pairs.inv_currency_pairs[df['currency_pair'].values[0]]
    df['current_spread'] = np.float64(df['highest_bid']) - np.float64(df['lowest_ask'].values[0])
    df['24_hr_spread'] = np.float64(df['24_hr_high']) - np.float64(df['24_hr_low'].values[0])
    df = df.set_index('timestamp')

    for t in currency_pairs.inv_currency_pairs:
        data_set[t].append(df.loc[df['currency_pair'] == t])

def discrete_update(bound):
    global data_set
    while True and time.time() < bound:
        if(time.time() % 5 == 0):
            for t in data_set:
                for t in data_set:
                    #load the old data
                    try:
                        old = pickle.load(open(f"data/first_overnight/individual/{t}.pkl"))
                    except:
                        print(f"File not found for {t}")
                        pickle.dump(data_set[t], open(f"data/first_overnight/individual/{t}.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
                    else:
                        #create the new data
                        new = old.append(data_set[t])

                        #create the new, blank repo to write the newer stream data to
                        data_set[t] = pd.DataFrame(columns = columns)
                        data_set[t] = data_set[t].set_index('timestamp')
                        #dump the old data
                        pickle.dump(new, open(f"data/first_overnight/individual/{t}.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
       
        else:
            time.sleep(1)

    for t in data_set:
        for t in data_set:
            #load the old data
            try:
                old = pickle.load(open(f"data/first_overnight/individual/{t}.pkl"))
            except:
                #print(f"File not found for {t}")
                pickle.dump(data_set[t], open(f"data/first_overnight/individual/{t}.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
            else:
                #create the new data
                new = old.append(data_set[t])

                #create the new, blank repo to write the newer stream data to
                data_set[t] = pd.DataFrame(columns = columns)
                data_set[t] = data_set[t].set_index('timestamp')
                #dump the old data
                pickle.dump(new, open(f"data/first_overnight/individual/{t}.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)


def streaming():
    global start
    #threading.Thread(target=thread_warning, args=(start,)).start()
    threading.Thread(target=discrete_update, args=(start,)).start()

    ws = websocket.WebSocket()
    ws.connect(base_url)

    formatted_request = {"command": "subscribe", "channel": 1002}
    ws.send(json.dumps(formatted_request))
    
    while True and time.time() < start +1.5:
        msg = json.loads(ws.recv())
        if(msg[0] == 1010):
            #We just recieved a heartbeat, the server is checking up on us to make sure we know its still there.
            print("Heartbeat") 
        elif(msg[0] == 1002):
            if(msg[1] == 1):
                #we just recieved our initial message.
                print("Initilized")
            else:
                threading.Thread(target=writing, args=(msg,)).start()

        else:
            pass

    ws.close()

streaming()

for t in currency_pairs.inv_currency_pairs:
    print(pickle.load(open(f"data/first_overnight/individual/{t}.pkl", "rb")))


print(data_set)


print("EOF")