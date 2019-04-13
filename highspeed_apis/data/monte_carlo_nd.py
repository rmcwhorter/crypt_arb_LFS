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
#import matplotlib.pyplot as plt
import random
import arrow

#funcs
def sign(a):
    if(a != 0):
        return np.abs(a)/a
    else:
        return 0

def arrow_random_from_range(min_t, max_t):
    #s = arrow.Arrow.range('minute', min_t, max_t)
    #p = 1.0/np.float64(len(s))
    return arrow.get(random.randint(0, max_t.timestamp - min_t.timestamp) + min_t.timestamp) #FAST AS FUCK BOIIIIIII, by about 6 orders of magnitude
    #random.randint(0,len(s))
    #return s[random.randint(0,len(s))] #SLIGHTLY FASTER, STILL SLOW AS FUCK
    '''
    flag = False
    while not flag:
        for r in range(len(s)):
            if random.random() < p: 
                return s[r]
                flag = True'''#SLOW AS FUCK

#DATA
base_url = 'monte_carlo_data/'
subset = "_MASSIVE_THIRD_"

currencies = ['qtumusdt','qtumbtc','btcusdt', 'qtumeth','ethbtc'] #we want to restructure this to trade btcusdt, because it is the least volatile and therefore* the most laggy
'''
1/(qtumbtc) * qtumusdt = btcusdt
1/ethbtc/qtumeth * qtumusdt = btcusdt
'''

extension = '.pkl'

data_dict = {}

for a in currencies:
    with open(base_url + a + subset + extension, 'rb') as handle: data_dict[a] = pickle.load(handle)

#PARAMETERS
#qtum   usdt
#['qtum/usdt', 'qtum/btc/btc/usdt', 'qtum/eth/eth/btc/btc/usdt']

trials = 3500
stdev_barrier = np.sqrt(2.0)
data_epoch = 24 #15 minutes
test_epoch = 24 # 15 mintues



min_data_time = np.min(data_dict['qtumusdt'].index.values)
max_test_time = np.max(data_dict['qtumusdt'].index.values)
for tick in data_dict:
    s = np.min(data_dict[a].index.values)
    t = np.max(data_dict[a].index.values)
    if(s > min_data_time): min_data_time = s #This insures that no matter how small we pick a time, we will have data for each ticker
    if(t < max_test_time): max_test_time = t

#Arrowize our max and min values
min_data_time = arrow.get(min_data_time)
max_test_time = arrow.get(max_test_time)
max_data_time = max_test_time.shift(minutes = -1 * test_epoch)

#Tests
k0 = [] #float
k1 = [] #float
mvmt = [] #1, 0, -1

print("Setting up Trials")

len_a = []
len_b = []
len_c = []
len_d = []
len_e = []

#SETUP THE TRIALS
for trial in range(trials):
    #Get our arrow times
    operands = {}
    test = {}

    flag = True
    while flag:
        data_start = arrow_random_from_range(min_data_time, max_data_time) #arrow timestamp
        data_end = data_start.shift(minutes = data_epoch)
        test_start = data_end
        test_end = test_start.shift(minutes = test_epoch)

        flag = False
        for tick in data_dict:
            l = data_dict[tick].loc[(data_dict[tick].index >= data_start.timestamp) & (data_dict[tick].index <= data_end.timestamp), 'close']
            if(len(l) < data_epoch-5): flag = True
            operands[tick] = l
        
        for tick in ['btcusdt']:#qtumusdt
            l = data_dict[tick].loc[(data_dict[tick].index >= test_start.timestamp) & (data_dict[tick].index <= test_end.timestamp), 'close']
            if(len(l) < data_epoch-5): flag = True
            test[tick] = l
    
    len_a.append(len(operands['qtumusdt']))
    len_b.append(len(operands['qtumbtc']))
    len_c.append(len(operands['btcusdt']))
    len_d.append(len(operands['qtumeth']))
    len_e.append(len(operands['ethbtc']))
        
    '''
    1/(qtumbtc) * qtumusdt = btcusdt
    1/ethbtc/qtumeth * qtumusdt = btcusdt
    '''
    
    #['qtum/usdt', 'qtum/btc/btc/usdt', 'qtum/eth/eth/btc/btc/usdt']
    k0.append((np.mean(operands['qtumusdt'].values)/np.mean(operands['qtumbtc'].values)) - np.mean(operands['btcusdt'].values))
    k1.append((np.mean(1/operands['ethbtc'].values) / np.mean(operands['qtumeth'].values) * np.mean(operands['qtumusdt'].values)) - np.mean(operands['btcusdt'].values))

    #k0.append((np.mean(operands['qtumbtc'].values)*np.mean(operands['btcusdt'].values)) - np.mean(operands['qtumusdt'].values))
    #k1.append((np.mean(operands['qtumeth'].values) * np.mean(operands['ethbtc'].values) * np.mean(operands['btcusdt'].values)) - np.mean(operands['qtumusdt'].values))

    slopes = []
    for s in range(1,len(test['btcusdt'].values)):
        #slopes.append((test['qtumusdt'].values[s]-test['qtumusdt'].values[0])/(s-0))
        slopes.append((test['btcusdt'].values[s]-test['btcusdt'].values[0])/(s-0))
    mvmt.append(np.mean(slopes))
    

print("Evaluating Trials")

#EVALUATE THE RESULTS OF THE TRIALS
mu_k1 = np.mean(k1)
s_k1 = np.std(k1)

mu_k0 = np.mean(k0)
s_k0 = np.std(k0)

mu_mvmt = np.mean(mvmt)
s_mvmt = np.std(mvmt)

mu_abs_mvmt = np.mean(np.abs(mvmt))
s_abs_mvmt = np.std(np.abs(mvmt))

pred = []

agg = []
longs = []
shorts = []
holds = []
physical_movement = []

for r in range(len(k0)):
    z0 = (k0[r] - mu_k0)/s_k0
    z1 = (k1[r] - mu_k1)/s_k1

    #z_mvmt = (mvmt[r] - mu_mvmt)/s_mvmt
    #z_abs_mvmt = (np.abs(mvmt[r]) - mu_abs_mvmt) / s_abs_mvmt

    if((z0 + z1)/2 > stdev_barrier and z0 > 0 and z1 > 0):
        if(mvmt[r] > 0):#stdev_barrier/2 #z_abs_mvmt > stdev_barrier/4 and 
            longs.append(1)
        else:
            longs.append(0)
        physical_movement.append(mvmt[r])

    elif((z0+z1)/2 < -1*stdev_barrier and z0 < 0 and z1 < 0):
        if(mvmt[r] < 0):#-1 * stdev_barrier / 2 #z_abs_mvmt > stdev_barrier/4 and 
            shorts.append(1)
        else:
            shorts.append(0)
        physical_movement.append(-1 * mvmt[r])

    else:
        if(True):
            holds.append(1)
        else:
            holds.append(0)

print()
print(mu_k0)
print(mu_k1)
print(np.mean((np.array(k0)+np.array(k1))/2))

print(np.corrcoef(k0,k1))
print()
print(sum(longs)/len(longs))
print(sum(shorts)/len(shorts))
print(sum(holds)/len(holds))
print(np.mean(physical_movement))

print()
print(len(longs))
print(len(shorts))
print((len(longs) + len(shorts))/trials)
print()
physical_movement = np.array(physical_movement)

print(np.prod(physical_movement + 1))
print()

for a in [len_a, len_b, len_c, len_d, len_e]:
    print()
    print(np.mean(a))
    print(np.median(a))
    print(np.min(a))
    print(np.std(a))

print()
for a in data_dict:
    print(a,": ", np.std(data_dict[a]['close']/data_dict[a]['open'] - 1))


print("EOF")