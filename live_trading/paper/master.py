print("SOF")
print()
print()

import os
import subprocess
import appscript
import sys
import time
import arrow as ar
import threading
import numpy as np

import position_handler as ph
import position as pos
import tracker
import lib
import pickle

lib.currencies = ['ltcusdt','btcusdt','ltcbtc']

'''
new_order = pos.position('huobi', 'ethusdt', 5, 1, -0.0005)
lib.blank_queue.append(new_order)
'''

lib.rts = 3600*5

thread_set = []

#Get our regular output up and running
thread_set.append(threading.Thread(target=lib.time_counter))

open_thread = threading.Thread(target=lib.open_trades)
open_thread.setName("OpenPositionHandler-Thread")

blank_thread = threading.Thread(target=lib.blank_trades)
blank_thread.setName("BlankPositionHandler-Thread")

thread_set.append(open_thread)
thread_set.append(blank_thread)

for currency in lib.currencies:
    t = threading.Thread(target=lib.tracking_func, args=(currency,))
    t.setName(currency + "-Tracker")
    thread_set.append(t)

algo_thread = threading.Thread(target=lib.algorithm)
algo_thread.setName("Algorithm-Thread")
thread_set.append(algo_thread)


for thread in thread_set:
    thread.start()

while True and len(thread_set) > 0: #and time.time() < lib.start + lib.rts
    time.sleep(10)
    for t in thread_set:
        if(not t.is_alive()):
            print(t.getName(), " has finished")
            t.join()
            thread_set.remove(t)

for a in lib.tracked_serurities_dict:
    print(lib.tracked_serurities_dict[a])



if(len(lib.closed_queue) > 0):
    delta = []
    for a in lib.closed_queue:
        delta.append(a.info.loc['Direction'][0] * (a.info.loc['Execution Price'][0] - a.info.loc['Sale Price'][0]))

    print(delta)
    print(np.mean(delta))
    print(np.median(delta))
    print(np.std(delta))
    print(np.prod(1+np.array(delta)))

'''


t2 = threading.Thread(target=lib.open_trades)
t1 = threading.Thread(target=lib.blank_trades)
thread_algo = threading.Thread(target=lib.algorithm)

currency_threads = []


t2.start()
t1.start()
thread_algo.start()
for thread in currency_threads:
    thread.start()

t2.join()
t1.join()

for a in currency_threads:
    a.join()

t0.join()

for open_order in range(len(lib.open_queue)):
    lib.close_position(lib.open_queue[open_order], open_counter=open_order)

for a in lib.tracked_serurities_dict:
    print()
    print(a)
    print(lib.tracked_serurities_dict[a])

k = np.mean(lib.tracked_serurities_dict['ltcusdt']['close'])/np.mean(lib.tracked_serurities_dict['btcusdt']['close']) - np.mean(lib.tracked_serurities_dict['ltcbtc']['close'])

delta = []
for a in lib.closed_queue:
    delta.append(a.info.loc['Direction'][0] * (a.info.loc['Execution Price'][0] - a.info.loc['Sale Price'][0]))

print(delta)
print(np.mean(delta))
print(np.median(delta))
print(np.std(delta))
print(np.prod(1+np.array(delta)))

'''

positions_dict = {
    "blank" : lib.blank_queue,
    "open" : lib.open_queue,
    "closed" : lib.closed_queue,
    "errorenous" : lib.erroneous_orders
}


with open("data/session_0/positions.pkl", 'wb') as handle: pickle.dump(positions_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open("data/session_0/ticker_logs.pkl", 'wb') as handle: pickle.dump(lib.tracked_serurities_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("EOF")