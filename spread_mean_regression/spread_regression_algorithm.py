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

spreads_z_scores = (spreads-mean)/stdev

ltcusdt_mvmt = ((ltcusdt['close'].values / ltcusdt['open'].values) - 1)
btcusdt_mvmt = ((btcusdt['close'].values / btcusdt['open'].values) - 1)
ltcbtc_mvmt = ((ltcbtc['close'].values / ltcbtc['open'].values) - 1)
combined_mvmt = ltcusdt_mvmt/btcusdt_mvmt
deriv_mvmt = (ltcusdt['close'].values*btcusdt_mvmt - btcusdt['close'].values*ltcusdt_mvmt)/(btcusdt_mvmt**2)

print(np.nan in deriv_mvmt)
print(np.nan in ltcbtc_mvmt)
print(len(deriv_mvmt))
print(len(ltcbtc_mvmt))

mpl.pyplot.figure(0)
mpl.pyplot.hist(spreads, bins=40)
mpl.pyplot.figure(1)
mpl.pyplot.hist(spreads_z_scores, bins=40)

mpl.pyplot.figure(4)
mpl.pyplot.plot(range(len(spreads)),spreads)
mpl.pyplot.figure(5)
mpl.pyplot.plot(range(len(spreads_z_scores)),spreads_z_scores)
mpl.pyplot.figure(6)
mpl.pyplot.plot(range(len(ltcusdt_mvmt)),ltcusdt_mvmt)
mpl.pyplot.plot(range(len(btcusdt_mvmt)),btcusdt_mvmt)
mpl.pyplot.plot(range(len(ltcbtc_mvmt)),ltcbtc_mvmt)
mpl.pyplot.figure(7)
mpl.pyplot.plot(range(len(ltcbtc_mvmt)),ltcbtc_mvmt)
mpl.pyplot.figure(8)
mpl.pyplot.plot(range(len(combined_mvmt)),combined_mvmt)
mpl.pyplot.figure(10)
mpl.pyplot.plot(range(len(deriv_mvmt)),deriv_mvmt)
mpl.pyplot.figure(9)
mpl.pyplot.plot(range(len(ltcbtc_mvmt)),ltcbtc_mvmt)
mpl.pyplot.plot(range(len(combined_mvmt)),combined_mvmt)
mpl.pyplot.figure(11)
mpl.pyplot.plot(range(len(ltcbtc_mvmt)),ltcbtc_mvmt)
mpl.pyplot.figure(12)
mpl.pyplot.plot(range(len(deriv_mvmt)),deriv_mvmt)

#Start to assemble the training dataset
#We're going to want these K values
#We're going to want 1 minute percent close/open for all three stocks
#We're going to want volume for all two stocks
#Thats probably a good start, we might add volatility later

#The testing data will be whether or not each of the three stocks went up by 


print("EOF")