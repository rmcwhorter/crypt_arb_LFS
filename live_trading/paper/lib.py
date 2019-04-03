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

latency = 1
rts = 60*10 #rts -> run time seconds
start = time.time()

tracked_serurities_dict = {}

blank_queue = []
open_queue = []
closed_queue = []
erroneous_orders = []

trading_flag = True

#ew_order = pos.position('huobi', 'ethusdt', 5, 1, -0.0005)

currencies = ['ethusdt', 'btcusdt', 'ethbtc']
#['ltcusdt','btcusdt','ltcbtc']
#['xlmbtc', 'ethbtc', 'xlmeth']
#ethxlm / 

def blank_trades():
    blank_counter = 0
    while True and trading_flag and time.time() < start+rts:

        time.sleep(latency)
        if(len(blank_queue) > 0):
            blank_counter = blank_counter % len(blank_queue)

            pointer = blank_queue[blank_counter]
            blank_summary = pointer.info()
            if(not blank_summary.loc['filled'].values[0]):
                #fill the position
                try:
                    blank_action = ph.open_position(pointer)
                    if(blank_action):
                        #order was filled successfully
                        #move the order from the blank_queue and put it into the open queue
                        open_queue.append(pointer)
                        del blank_queue[blank_counter]
                except:
                    print()
                    print("===== blank_trades =====")
                    print("An error was encountered processing " + str(blank_summary.loc['Literal Direction'].values[0]) + " " + str(blank_summary.loc['Security'].values[0]) + " on " + str(blank_summary.loc['Exchange'].values[0]))
                    print("Security was ordered at " + str(blank_summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")))
                    print("===== blank_trades =====")
                    print()
                else:
                    print()
                    print("===== blank_trades =====")
                    print('\t' + 'Order successfully processed')
                    print("===== blank_trades =====")
                    print()

            elif(blank_summary.loc['filled'].values[0]):
                try:
                    open_queue.append(pointer)
                    del blank_queue[blank_counter]
                except Exception as e:
                    print()
                    print("===== blank_trades =====")
                    print("An error was encountered processing " + str(blank_summary.loc['Literal Direction'].values[0]) + " " + str(blank_summary.loc['Security'].values[0]) + " on " + str(blank_summary.loc['Exchange'].values[0]))
                    print("Security was ordered at " + str(blank_summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")))
                    print("===== blank_trades =====")
                    print()
                    print(e)
                    print()
                else:
                    print()
                    print("===== blank_trades =====")
                    print('\t' + 'Order successfully moved')
                    print("===== blank_trades =====")
                    print()
            else:
                print()
                print("===== blank_trades =====")
                print("An error was encountered processing " + str(blank_summary.loc['Literal Direction'].values[0]) + " " + str(blank_summary.loc['Security'].values[0]) + " on " + str(blank_summary.loc['Exchange'].values[0]))
                print("Security was ordered at " + str(blank_summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")))
                print("===== blank_trades =====")
                print()
                #an error has occured
        else:
            #print("blank_trades running on " + blank_thread + " currently has " + str(len(open_queue)) + " jobs to preform.")
            blank_counter = -1
        blank_counter += 1

def open_trades():
    open_counter = 0
    while True and time.time() < start+rts:
        time.sleep(latency)

        if(len(open_queue) > 0):
            open_counter = open_counter % len(open_queue)

            local_order = open_queue[open_counter]

            summary = local_order.info()
            if(summary.loc["Arrow Terminal Time"].values[0] < ar.utcnow().span('microsecond')[0].to("US/Central")):
                try:
                    close_position(local_order, open_counter=open_counter)
                except Exception as e:
                    print()
                    print("===== open_trades =====")
                    print("An error was encountered processing " + str(summary.loc['Literal Direction'].values[0]) + " " + str(summary.loc['Security'].values[0]) + " on " + str(summary.loc['Exchange'].values[0]))
                    print("Security was ordered at " + str(summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")))
                    print("===== open_trades =====")
                    print()
                    print(e)
                    print()
                    print(summary)
                    print()
                    for zeta in tracked_serurities_dict:
                        print(tracked_serurities_dict[zeta])
                    print()
                else:
                    open_counter += -1
                    print()
                    print("===== open_trades =====")
                    print('\t' + 'Order successfully processes')
                    print("===== open_trades =====")
                    print()
            else:
                #Order has not yet reached maturity.
                pass
                #check if we should act on the position for other reasons than the order has reached termination
        else:
            #print("open_trades running on " + open_thread + " currently has " + str(len(open_queue)) + " jobs to preform.")
            open_counter = -1

        open_counter += 1

def tracking_func(name):
    global tracked_serurities_dict
    t = tracker.tracker('huobi', name)
    tracked_serurities_dict[name] = []
    t.begin_tracking()
    while True and time.time() < start+rts:
        time.sleep(0.1)
        try:
            tracked_serurities_dict[name] = t.data
        except:
            print()
            print("===== tracking_func =====")
            print('\t' + 'A failed was encountered writing ' + name + ' to memory.')
            print("===== tracking_func =====")
            print()
        else:
            pass
    t.end_tracking()
    print(t.flag)

def time_counter():
    local_time = time.time()
    while True and local_time < start + rts:
        time.sleep(15)
        print()
        print("===== time_counter =====")
        print("Time: ",int(local_time - start))
        print('\t', 'Blank: ', len(blank_queue))
        print('\t', 'Open: ', len(open_queue))
        print('\t', 'Closed: ', len(closed_queue))
        print('\t', 'Erroneous: ', len(erroneous_orders))
        print("===== time_counter =====")
        print()

def close_position(local_order, open_counter=None):
    action = ph.close_position(local_order)
    if(action):
        closed_queue.append(local_order) #move the position from the open queue to the closed queue
        del open_queue[open_counter]

def algorithm(k_mu = 0.00012239861238334584, k_sigma = 0.0032892491919637194, stdev_barrier = 1.25, epoch_seconds = 60, currencies=currencies):
    time.sleep(int(epoch_seconds))
    position_count = 0
    delay = 0
    while True and time.time() < start + rts and position_count < 10:
        time.sleep(int(15 + delay)) #We only really need to update our estimates every 15 seconds, and unlike merely writing to and from memory, this algo will likely be a bit CPU intensive. Maybe.

        #We need to get the last 15 minutes of data for each currency
        pointer_time = ar.utcnow().span('microsecond')[0].to("US/Central").shift(seconds= -1*epoch_seconds)

        operands = {}

        for c in currencies:
            index = tracked_serurities_dict[c].index.where(tracked_serurities_dict[c].index > pointer_time).dropna()
            if(len(index.values) == 0): 
                print(index)
                operands[c] = tracked_serurities_dict[c].loc[index]
        
        if(len(operands[currencies[0]]) > 0 and len(operands[currencies[1]]) > 0 and len(operands[currencies[2]]) > 0):
            f = np.mean(operands[currencies[0]]['close'].values)
            g = np.mean(operands[currencies[1]]['close'].values)
            h = np.mean(operands[currencies[2]]['close'].values)


            k = (f/g)-h

            z_k = (k-k_mu)/k_sigma
            if(True):#np.abs(z_k) > stdev_barrier
                    #trade on it
                try:
                    if(z_k > 0):
                            #queue a long position with an expiry time of 1 epoch
                        new_position = pos.position('huobi', currencies[-1], 1, 1, k)
                        blank_queue.append(new_position)
                    else:
                            #queue a short position with an expiry time of 1 epoch
                        new_position = pos.position('huobi', currencies[-1], 1, -1, k)
                        blank_queue.append(new_position)
                    position_count += 1
                except:
                    print()
                    print("===== algorithm =====")
                    print('\t' + "Algorithm has encountered a failure")
                    print("===== algorithm =====")
                    print()
                else:
                    print()
                    print("===== algorithm =====")
                    print('\t' + "Algorithm has successfully queued a trade")
                    print("===== algorithm =====")
                    print()
                delay = int(epoch_seconds/5)
            else:
                    delay = 0
        else:
            pass


    pass