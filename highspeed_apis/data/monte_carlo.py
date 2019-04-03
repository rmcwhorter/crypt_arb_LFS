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
import random
import algo_lib

current_algo = algo_lib.conservation_algo_improved_15_epoch


base_url = 'monte_carlo_data/'
descriptor = "_MASSIVE_"
currencies = ['ltcusdt','btcusdt','ltcbtc'] #['btcusdt','ethusdt','ethbtc'] #
extension = '.pkl'

data_dict = {}

for a in currencies:
    with open(base_url + a + descriptor + extension, 'rb') as handle: data_dict[a] = pickle.load(handle)
    
movement_quote_a = []
movement_quote_b = []
movement_quote_c = []

predictions_quote_a = []
predictions_quote_b = []
predictions_quote_c = []

successes_a = []
successes_b = []
successes_c = []

successes = []

epoch = 20 #15 minute intervals
full_interval = data_dict[currencies[-1]].index.values
data_interval = full_interval[0:-1-epoch-epoch]
indices_data_interval = range(len(data_interval))

samples = 10000

for a in range(samples):
    data_start = random.choice(indices_data_interval)
    data_end = data_start + epoch
    
    trade_start = data_end
    trade_end = trade_start + epoch
    
    #Data during the prediction period
    quote_a_data = np.array(data_dict[currencies[0]]['close'][data_start:data_end].values)
    quote_b_data = np.array(data_dict[currencies[1]]['close'][data_start:data_end].values)
    quote_c_data = np.array(data_dict[currencies[-1]]['close'][data_start:data_end].values)
    
    #Data during the trading period
    quote_a_trade = np.array(data_dict[currencies[0]]['close'][trade_start:trade_end].values)
    quote_b_trade = np.array(data_dict[currencies[1]]['close'][trade_start:trade_end].values)
    quote_c_trade = np.array(data_dict[currencies[-1]]['close'][trade_start:trade_end].values)
    
    
    #movements during the trading period
    interval_movement_quote_a = ((np.mean(quote_a_trade) / quote_a_trade[0]) - 1) * 100
    interval_movement_quote_b = ((np.mean(quote_b_trade) / quote_b_trade[0]) - 1) * 100
    interval_movement_quote_c = ((np.mean(quote_c_trade) / quote_c_trade[0]) - 1) * 100
    
    movement_quote_a.append(interval_movement_quote_a)
    movement_quote_b.append(interval_movement_quote_b)
    movement_quote_c.append(interval_movement_quote_c)
    
    k = current_algo(quote_a_data, quote_b_data, quote_c_data, invert_c = False, stdev = 6.895029464147693/(10**5), mu = -0.0007422856842497092, stdev_boundary = 3)
    
    predictions_quote_a.append(-1 * k)
    predictions_quote_b.append(-1 * k)
    predictions_quote_c.append(k)
    
for index in range(len(predictions_quote_c)):
    successes_c.append(0.5 * np.sign(predictions_quote_c[index]) * movement_quote_c[index])
    successes_b.append(0.25 * np.sign(predictions_quote_b[index]) * movement_quote_b[index])
    successes_a.append(0.25 * np.sign(predictions_quote_a[index]) * movement_quote_a[index])

#filter out non-trades
k_filter = []
movement_filter = []
for a in range(len(predictions_quote_c)):
    if(predictions_quote_c[a] != 0):
        k_filter.append(predictions_quote_c[a])
        movement_filter.append(movement_quote_c[a])


print(np.mean(successes_c))
print(np.median(successes_c))
print(np.std(successes_c))
print()
print(np.sum(predictions_quote_c))
print(np.mean(predictions_quote_c))
print(np.median(predictions_quote_c))
print(np.std(predictions_quote_c))
print()
print(np.sum(successes_c)+np.sum(successes_b) + np.sum(successes_a))
mpl.pyplot.figure(0)
mpl.pyplot.scatter(k_filter, movement_filter)
print()
print(np.corrcoef(movement_quote_c,predictions_quote_c))
print(np.corrcoef(movement_quote_b,predictions_quote_b))
print(np.corrcoef(movement_quote_a,predictions_quote_a))
print(np.corrcoef(movement_filter,k_filter))
print()
mpl.pyplot.figure(1)
mpl.pyplot.scatter(predictions_quote_c, movement_quote_c)


print('EOF')