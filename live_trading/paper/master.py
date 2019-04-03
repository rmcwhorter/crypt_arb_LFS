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

new_order = pos.position('huobi', 'ethusdt', 5, 1, -0.0005)
    
t0 = threading.Thread(target=lib.time_counter)
t0.start()

t2 = threading.Thread(target=lib.open_trades)
t1 = threading.Thread(target=lib.blank_trades)
thread_algo = threading.Thread(target=lib.algorithm)

currency_threads = []
for currency in lib.currencies:
    currency_threads.append(threading.Thread(target=lib.tracking_func, args=(currency,)))

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
