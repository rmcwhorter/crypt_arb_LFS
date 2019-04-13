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
import arrow as ar

def sign(a):
    if(a != 0):
        return np.abs(a)/a
    else:
        return 0

def actual(timeseries, purchase_price):
    out = 0
    if(np.mean(timeseries) > purchase_price and np.max(timeseries) > purchase_price):
        out = (1, np.max(timeseries))
    elif(np.mean(timeseries) < purchase_price and np.min(timeseries) < purchase_price):
        out = (-1, np.min(timeseries))
    else:
        out = (0,0)
    return out

def predicted(k, mu_k, stdev_k, barrier, epoch=None):
    if(type(k) == np.float64):
        k_aggregate = k
    else:
        k_aggregate = np.sum(k)
        epoch = len(k)
    z_score = (k_aggregate - mu_k)/stdev_k

    if(np.abs(z_score) > barrier or np.abs(z_score) == barrier):
        out = (sign(z_score), z_score, k_aggregate)
    elif(np.abs(z_score) < barrier):
        out = (0, z_score, k_aggregate)
    return out 



base_url = 'monte_carlo_data/'
subset = "_MASSIVE_THIRD_"

currencies = ['qtumbtc','btcusdt', 'qtumusdt']
extension = '.pkl'

'''
base_url = 'monte_carlo_data/'
subset = "_MASSIVE_"

currencies = ['ltcusdt','btcusdt','ltcbtc']  #['btcusdt','ethusdt','ethbtc']
extension = '.pkl'
'''

data_dict = {}

for a in currencies:
    with open(base_url + a + subset + extension, 'rb') as handle: data_dict[a] = pickle.load(handle)
    
data_epochs = 10
test_epochs = 1

mu = 0.0006036385349623667 #substituting measured mean for otherwise assumed zero
stdev_barrier = 1.25
trials = 10000

max_data_epochs = 6

sum_trials = 0
sum_actionable_trades = 0

#Metric Arrays
indices = []
long_percent_correct_metric = []
short_percent_correct_metric = []
no_position_correct_prediction = []
aggregate_position_taken_percent_correct = []
aggregate_correct_percent = []
garbage_as_percent_of_total = []
aggregate_actionable_trades = []
aggregate_trials = []
aggregate_actionable_percent_total = []
barriers = []
k_mu_array = []
k_stdev_array = []

for stdev_barrier in [1,1.25,1.5,2]:#[stdev_barrier] #[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
    for data_epochs in range(1,2): #max_data_epochs+1
        for epochs in range(15,25):
            full_interval = data_dict[currencies[-1]].index.values
            data_interval = full_interval[0:-1-((data_epochs + test_epochs) * epochs)]
            indices_data_interval = range(len(data_interval))
            
            tmp_k = []
            tmp_z_scores = []

            tmp_direction_movements = []
            tmp_closure_price = []

            predicted_direction = []

            for a in range(trials):
                sum_trials += 1
                
                data_start = random.choice(indices_data_interval)
                data_end = data_start + (data_epochs * epochs)
                
                trade_start = data_end
                trade_end = trade_start + (test_epochs * epochs)
                
                x = data_dict[currencies[-1]]['close'][full_interval[trade_end]]
                y = data_dict[currencies[-1]]['close'][full_interval[trade_start]] == np.nan
                
                while(type(x) == pd.core.series.Series or type(y) == pd.core.series.Series):
                    data_start = random.choice(indices_data_interval)
                    data_end = data_start + epochs
                    
                    trade_start = data_end
                    trade_end = trade_start + epochs
                    
                    x = data_dict[currencies[-1]]['close'][full_interval[trade_end]]
                    y = data_dict[currencies[-1]]['close'][full_interval[trade_start]] == np.nan
                    
                
                #predict k 
                a = np.array(data_dict[currencies[0]]['close'][data_start:data_end].values)
                b = np.array(data_dict[currencies[1]]['close'][data_start:data_end].values)
                c = np.array(data_dict[currencies[-1]]['close'][data_start:data_end].values)

                #compute k
                k = np.sum((a*b)-c)            
                tmp_k.append(k)

                #compute actual
                #np.array(data_dict[currencies[0]]['close'][data_start:data_end].values)
                df = np.array(data_dict[currencies[-1]]['close'][trade_start:trade_end].values)
                purchase_price = data_dict[currencies[-1]]['open'][trade_start:trade_start+1].values[0]
                #print(df)
                #print(purchase_price)
                act = actual(df, purchase_price)
                tmp_direction_movements.append(act[0])
                tmp_closure_price.append(act[1])


            
            mu = np.mean(tmp_k)
            k_stdev = np.std(tmp_k)
            
            for a in range(len(tmp_k)):
                #predicted(k, mu_k, stdev_k, barrier) -> (sign(z_score), z_score, k_aggregate)
                pred = predicted(tmp_k[a], mu, k_stdev, stdev_barrier, epochs)

                predicted_direction.append(pred[0])
                tmp_z_scores.append(pred[1])

            long_trials = 0
            long_successes = 0

            short_trials = 0
            short_successes = 0

            no_pos_trials = 0
            no_pos_successes = 0

            for row in range(len(tmp_direction_movements)):
                if(predicted_direction[row] == 1.0):
                    long_trials += 1
                    if(predicted_direction[row] - tmp_direction_movements[row] == 0):
                        long_successes += 1
                elif(predicted_direction[row] == -1.0):
                    short_trials += 1
                    if(predicted_direction[row] - tmp_direction_movements[row] == 0):
                        short_successes += 1
                elif(predicted_direction[row] == 0.0):
                    no_pos_trials += 1
                    if(predicted_direction[row] - tmp_direction_movements[row] == 0):
                        no_pos_successes += 1

            sum_actionable_trades += long_trials + short_trials

            print("STDEV Barrier: ", stdev_barrier)
            print("Data Epochs per Test Epoch: ", data_epochs)
            print('\t',"Epoch Duration: ",epochs)
            print('\t', str(data_epochs * epochs) + " prediciting " + str(epochs))
            print("\t\t", "Mean k for this epoch ", mu)
            print("\t\t", "Stdev K for this epoch ", k_stdev)
            print("\t\t", "Mean Z Score for this set ", np.mean(tmp_z_scores))
            print()
            print('\t\t','Success Rates: ')
            print('\t\t\t',"Long % Correct: ", long_successes/long_trials * 100)
            print('\t\t\t',"Short % Correct: ", short_successes/short_trials * 100 )
            print('\t\t\t',"Aggregate Position Taken Correct: ", (long_successes + short_successes)/(short_trials + long_trials) * 100)
            print('\t\t\t',"Aggregate Correct Prediction: ", (no_pos_successes + long_successes + short_successes)/(no_pos_trials + short_trials + long_trials) * 100)
            print('\t\t\t',"No Position % Correct: ", no_pos_successes/no_pos_trials * 100 )
            print()
            print('\t\t\t',"Actual Garbage as Percent of Actuals: ", no_pos_trials / (no_pos_trials + short_trials + long_trials) * 100)
            print()
            print('\t\t', "Actionable Trades: ", long_trials + short_trials)
            print('\t\t', "Trials: ",sum_trials)
            print("\t\t", "Sum Actionable Trades: ", sum_actionable_trades)
            print()

            #Metric records
            indices.append(str(data_epochs * epochs) + " predicting " + str(epochs))
            long_percent_correct_metric.append(long_successes/long_trials * 100)
            short_percent_correct_metric.append(short_successes/short_trials * 100)
            no_position_correct_prediction.append(no_pos_successes/no_pos_trials * 100)
            aggregate_position_taken_percent_correct.append((long_successes + short_successes)/(short_trials + long_trials) * 100)
            aggregate_correct_percent.append((no_pos_successes + long_successes + short_successes)/(no_pos_trials + short_trials + long_trials) * 100)
            garbage_as_percent_of_total.append(no_pos_trials / (no_pos_trials + short_trials + long_trials) * 100)
            aggregate_actionable_trades.append(long_trials + short_trials)
            aggregate_trials.append(long_trials + short_trials + no_pos_trials)
            aggregate_actionable_percent_total.append((long_trials + short_trials)/(long_trials + short_trials + no_pos_trials)*100)
            barriers.append(stdev_barrier)
            k_mu_array.append(mu)
            k_stdev_array.append(k_stdev)

d = {}
h = ["Long Correct [%]", "Short Correct [%]", "No Pos Correct [%]", "Long + Short Correct [%]", "Total Correct [%]", "Garbage of Total [%]", "Actionable Trades [N]", "Trials [N]", "Actionable of Total [%]", "STDEV Barrier [R]", "K Mu", "K STDEV"]
j = [long_percent_correct_metric, short_percent_correct_metric, no_position_correct_prediction, aggregate_position_taken_percent_correct, aggregate_correct_percent, garbage_as_percent_of_total, aggregate_actionable_trades, aggregate_trials, aggregate_actionable_percent_total, barriers, k_mu_array, k_stdev_array]
for a in range(len(j)):
    d[h[a]] = j[a]

out_df = pd.DataFrame(data=d, index=indices)

lt = ar.utcnow().span('microsecond')[0].to("US/Central").format("YYYY-MM-DD HH-mm-ss SSSS ZZ")

with open("result_data/" + "master_output_" + lt + ".pkl", 'wb') as handle: pickle.dump(out_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
out_df.to_excel("excel_summaries/" + "master_output_" + currencies[0] + "_" + currencies[1] + "_" + currencies[2] + "_" +lt + ".xlsx")
'''
indices = []
long_percent_correct_metric = []
short_percent_correct_metric = []
no_position_correct_prediction = []
aggregate_position_taken_percent_correct = []
aggregate_correct_percent = []
garbage_as_percent_of_total = []'''



print('EOF')