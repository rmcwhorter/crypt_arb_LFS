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
from functools import reduce
import statsmodels.tsa.stattools as ts


base_url = '../highspeed_apis/data/monte_carlo_data/'
descriptor = "_MASSIVE_"
currencies = ['ltcusdt','btcusdt','ltcbtc'] #['btcusdt','ethusdt','ethbtc'] #
extension = '.pkl'

data_dict = {}

def slip_correlation(arr1, arr2, index = 100):
    corrcoeffs = []
    for slip in range(1,index+1):
        tmp_arr1 = arr1[:-slip]
        tmp_arr2 = arr2[slip:]
        corrcoeffs.append(np.corrcoef(tmp_arr1,tmp_arr2)[0][1])
    return corrcoeffs

def limiting_mean(arr):
    out = []
    for a in range(len(arr)):
        out.append(np.mean(arr[0:a]))
    return out

def hurst(ts):
	"""Returns the Hurst Exponent of the time series vector ts"""
	# Create the range of lag values
	lags = range(2, 100)

	# Calculate the array of the variances of the lagged differences
	tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]

	# Use a linear fit to estimate the Hurst Exponent
	poly = np.polyfit(np.log(lags), np.log(tau), 1)

	# Return the Hurst exponent from the polyfit output
	return poly[0]*2.0

for a in currencies:
    with open(base_url + a + descriptor + extension, 'rb') as handle: data_dict[a] = pickle.load(handle)

ltcusdt_raw = data_dict['ltcusdt']
btcusdt_raw = data_dict['btcusdt']
ltcbtc_raw = data_dict['ltcbtc']

'''
print(len(ltcusdt))
print(len(btcusdt))
print(len(ltcbtc))
'''

#print(ltcbtc - (ltcusdt/btcusdt))

index_intersection = reduce(np.intersect1d, (ltcusdt_raw.index.values, btcusdt_raw.index.values, ltcbtc_raw.index.values))
    
ltcusdt_duplicates = ltcusdt_raw.loc[index_intersection]
btcusdt_duplicates = btcusdt_raw.loc[index_intersection]
ltcbtc_duplicates = ltcbtc_raw.loc[index_intersection]

ltcusdt = ltcusdt_duplicates[~ltcusdt_duplicates.index.duplicated(keep='first')]
btcusdt = btcusdt_duplicates[~btcusdt_duplicates.index.duplicated(keep='first')]
ltcbtc = ltcbtc_duplicates[~ltcbtc_duplicates.index.duplicated(keep='first')]
    
spreads = ltcbtc['close'].values - (ltcusdt['close'].values/btcusdt['close'].values)
    
mean = np.mean(spreads)
median = np.median(spreads)
stdev = np.std(spreads)

print(mean)
print(median)
print(mean - median)
print(stdev)
print()

inc = (ltcbtc['close']/ltcbtc['open'] - 1)*100

inc_mean = np.mean(inc)
inc_median = np.median(inc)
inc_stdev = np.std(inc)

mvmt = np.abs(inc)

mvmt_mean = np.mean(mvmt)
mvmt_median = np.median(mvmt)
mvmt_stdev = np.std(mvmt)

print(inc_mean)
print(inc_median)
print(inc_mean - inc_median)
print(inc_stdev)
print()

print(mvmt_mean)
print(mvmt_median)
print(mvmt_mean - mvmt_median)
print(mvmt_stdev)






high_stdev_spreads = []
indices = []
high_stdev_movement = []
high_stdev_movement_abs = []

result = ts.adfuller(ltcbtc['close'].values, 1)
print("ADF: ", result)
hurst_result = hurst(ltcbtc['close'].values)
print("HURST: ", hurst_result)
print("SPREAD HURST: ", hurst(spreads))

gbm = np.log(np.cumsum(np.random.randn(100000))+1000)
mr = np.log(np.random.randn(100000)+1000)
tr = np.log(np.cumsum(np.random.randn(100000)+1)+1000)

print("HURST GBM: ", hurst(gbm))
print("HURST MR: ", hurst(mr))
print("HURST TR: ", hurst(tr))

#mpl.pyplot.plot(range(len(index_intersection)),inc)
print(np.corrcoef(inc,spreads))

count = 0

for spread in spreads:
    if((spread - mean)/stdev > 2):
        high_stdev_spreads.append(spread)
        indices.append(index_intersection[count])
        high_stdev_movement.append((ltcbtc['close'].loc[index_intersection[count]]/ltcbtc['open'].loc[index_intersection[count]] - 1)*100)
        high_stdev_movement_abs.append(np.abs((ltcbtc['close'].loc[index_intersection[count]]/ltcbtc['open'].loc[index_intersection[count]] - 1)*100))
    
    count += 1

print(np.corrcoef(high_stdev_spreads,high_stdev_movement))
print(np.corrcoef(high_stdev_spreads,high_stdev_movement_abs))


slip_correl = slip_correlation(spreads,inc)

mpl.pyplot.figure(0)
mpl.pyplot.hist(spreads, bins=40)
mpl.pyplot.figure(1)
mpl.pyplot.hist(inc, bins=40)
mpl.pyplot.figure(2)
mpl.pyplot.hist(mvmt, bins=40)

mpl.pyplot.figure(4)
mpl.pyplot.plot(range(len(index_intersection)),ltcbtc['close'].values)
mpl.pyplot.plot(range(len(index_intersection)),ltcusdt['close'].values/btcusdt['close'].values)

mpl.pyplot.figure(5)
mpl.pyplot.plot(range(len(index_intersection)),spreads)
mpl.pyplot.figure(99)
mpl.pyplot.plot(range(len(index_intersection)),limiting_mean(spreads))

mpl.pyplot.figure(6)
mpl.pyplot.plot(range(len(indices)),high_stdev_spreads)
mpl.pyplot.figure(7)
mpl.pyplot.plot(range(len(indices)),high_stdev_movement)
mpl.pyplot.figure(8)
mpl.pyplot.plot(range(len(slip_correl)),slip_correl)
mpl.pyplot.plot(range(len(slip_correl)),limiting_mean(slip_correl))
mpl.pyplot.figure(9)
mpl.pyplot.hist(ltcbtc['vol'].values, bins=40)
mpl.pyplot.figure(10)
mpl.pyplot.hist(ltcbtc['amount'].values, bins=40)
  


print('EOF')