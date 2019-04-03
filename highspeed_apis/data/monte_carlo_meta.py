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


base_url = 'monte_carlo_data/'
subset = "_MASSIVE_"

currencies = ['ltcusdt','btcusdt','ltcbtc']  #['btcusdt','ethusdt','ethbtc']
extension = '.pkl'

data_dict = {}

for a in currencies:
    with open(base_url + a + subset + extension, 'rb') as handle: data_dict[a] = pickle.load(handle)
    
data_epochs = 10
test_epochs = 1

mu = 0.0006036385349623667 #substituting measured mean for otherwise assumed zero
stdev_barrier = 1.75
trials = 15000

max_data_epochs = 6

sum_trials = 0
sum_actionable_trades = 0

k_values = []
k_values_time_adjusted_data = []
k_values_time_adjusted_test = []
k_values_time_adjusted_total = []
results = []
results_time_adjusted = []
rates = []
rates_correlates = []
cagrs = []
returns_time_percent = []


for h in range(1,max_data_epochs+1):
    data_epochs = h
    for z in range(1,40):
        
        movements = []
        predictions = []
        successes = []
    
        epoch = z #15 minute intervals
        full_interval = data_dict[currencies[-1]].index.values
        data_interval = full_interval[0:-1-((data_epochs + test_epochs) * epoch)]
        indices_data_interval = range(len(data_interval))
        
        #print("Len full interval ", len(full_interval))
        #print("Len data interval ", len(data_interval))
        tmp_k = []
        tmp_movements = []
        tmp_successes = []
        tmp_successful_movements = []
        for a in range(trials):
            sum_trials += 1
            #if(a % 1000 == 0): print("\t\t\t",a/100000 * 100, "%")
            
            data_start = random.choice(indices_data_interval)
            data_end = data_start + (data_epochs * epoch)
            
            trade_start = data_end
            trade_end = trade_start + (test_epochs * epoch)
            
            x = data_dict[currencies[-1]]['close'][full_interval[trade_end]]
            y = data_dict[currencies[-1]]['close'][full_interval[trade_start]] == np.nan
            
            while(type(x) == pd.core.series.Series or type(y) == pd.core.series.Series):
                data_start = random.choice(indices_data_interval)
                data_end = data_start + epoch
                
                trade_start = data_end
                trade_end = trade_start + epoch
                
                x = data_dict[currencies[-1]]['close'][full_interval[trade_end]]
                y = data_dict[currencies[-1]]['close'][full_interval[trade_start]] == np.nan
                
                
                
                
                
            movement = (data_dict[currencies[-1]]['close'][full_interval[trade_end]] / data_dict[currencies[-1]]['close'][full_interval[trade_start]] - 1) * 100
            
            
            
            
            movements.append(movement)
            tmp_movements.append(movement)
            results.append(movement)
            results_time_adjusted.append(movement/(test_epochs * z))
            
            #predict k 
            a = np.array(data_dict[currencies[0]]['close'][data_start:data_end].values)
            b = np.array(data_dict[currencies[1]]['close'][data_start:data_end].values)
            c = np.array(data_dict[currencies[-1]]['close'][data_start:data_end].values)
            
            k = np.sum((a/b)-c)
            
            predictions.append(k)
            
            tmp_k.append(k)

            k_values.append(k)
            k_values_time_adjusted_data.append(k/(data_epochs * z))
            k_values_time_adjusted_test.append(k/(test_epochs * z))
            k_values_time_adjusted_total.append(k/((data_epochs + test_epochs) * z))
        
        mu = np.mean(tmp_k)
        k_stdev = np.std(tmp_k)
        tmp_z_scores = []
        tmp_successful_movements = []
        for a in range(len(tmp_movements)):
            z_score = (tmp_k[a] - (mu))/k_stdev
            tmp_z_scores.append(z_score)
            if(np.abs(z_score) > stdev_barrier):
                sign_movement = np.abs(tmp_movements[a])/tmp_movements[a]
                sign_prediction = np.abs(tmp_k[a] - mu)/(tmp_k[a] - mu)
                tmp_successful_movements.append(tmp_movements[a])
                
                
                
                '''
                if(type(sign_movement) == pd.core.series.Series):
                    print(sign_movement)
                if(type(sign_prediction) == pd.core.series.Series):
                    print(sign_prediction)
                '''
                if(sign_movement == sign_prediction):
                    successes.append(1)
                    tmp_successes.append(1)
                else:
                    successes.append(0)
                    tmp_successes.append(0)
        
        sum_actionable_trades += len(tmp_successes)

        rtp_raw = ((np.sum(tmp_successes)/len(tmp_successes)) - (1-(np.sum(tmp_successes)/len(tmp_successes))))*(1+(np.mean(np.abs(tmp_movements)) / epoch / 100))**epoch
        cagr = ((1+rtp_raw)**(1/epoch)) - 1

        cagrs.append(cagr)
        returns_time_percent.append(rtp_raw)

        print("Data Epochs per Test Epoch: ", data_epochs)
        print('\t',"Epoch Duration: ",z)
        print('\t', str(data_epochs * epoch) + " prediciting " + str(epoch))
        #print('\t',movements)
        #print('\t',predictions)
        #print('\t',successes)
        print('\t\t', "Actionable Trades: ", len(tmp_successes))
        print('\t\t','Average % movement per minute: ',np.mean(tmp_movements) / epoch)
        print('\t\t','Average % |movement| per minute for successful trades: ',np.mean(np.abs(tmp_movements)) / epoch)
        print("\t\t", "Mean k for this epoch ", mu)
        print("\t\t", "Stdev K for this epoch ", k_stdev)
        print("\t\t", "Mean Z Score for this set ", np.mean(tmp_z_scores))
        print()
        print('\t\t','Success Rate: ',np.sum(tmp_successes)/len(tmp_successes) * 100,'%')
        print("\t\t", "Expected average return over the full time period: ", rtp_raw)
        print("\t\t", "Expected CAGR, per minute basis: ", cagr)
        print()
        print("\t\tTrials: ",sum_trials)
        print("\t\t", "Sum Actionable Trades: ", sum_actionable_trades)
        print()

        rates.append(np.sum(tmp_successes)/len(tmp_successes) * 100)
        rates_correlates.append(str(data_epochs * epoch) + " prediciting " + str(epoch))

with open(str("k_values_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(k_values, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("k_values_time_adjusted_data_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(k_values_time_adjusted_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("k_values_time_adjusted_test_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(k_values_time_adjusted_test, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("k_values_time_adjusted_total_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(k_values_time_adjusted_total, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("results_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("results_time_adjusted_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(results_time_adjusted, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("rates_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(rates, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("rates_correlate_new" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(rates_correlates, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("cagrs" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(cagrs, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(str("rtps" + str(stdev_barrier) +'.pkl'), 'wb') as handle: pickle.dump(returns_time_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)

print(rates)
print(np.max(rates))
print(rates_correlates[np.argmax(rates)])


print('EOF')