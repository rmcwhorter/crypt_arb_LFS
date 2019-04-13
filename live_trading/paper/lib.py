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

def init():
    pass
    for c in currencies:
        tracked_serurities_dict[c] = []

def func_print(instr):
    if(type(instr) == str):
        print("===== " + str(threading.current_thread().ident) + " =====")
        print('\t',instr)
        print()
    elif(type(instr) == list):
        print("===== " + str(threading.current_thread().ident) + " =====")
        for s in instr:
            print('\t',str(s))
        print()
    else:
        print("EXCEPTION OCCURED: ")
        print("TYPE OF ", type(instr))

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
                    out_string = [
                        str("An error was encountered processing " + str(blank_summary.loc['Literal Direction'].values[0]) + " " + str(blank_summary.loc['Security'].values[0]) + " on " + str(blank_summary.loc['Exchange'].values[0])),
                        str("Security was ordered at " + str(blank_summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")))
                    ]
                    func_print(out_string)

                else:
                    func_print('Order successfully processed')

            elif(blank_summary.loc['filled'].values[0]):
                try:
                    open_queue.append(pointer)
                    del blank_queue[blank_counter]
                except Exception as e:

                    out_string = [
                        str("An error was encountered processing " + str(blank_summary.loc['Literal Direction'].values[0]) + " " + str(blank_summary.loc['Security'].values[0]) + " on " + str(blank_summary.loc['Exchange'].values[0])),
                        str("Security was ordered at " + str(blank_summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ"))),
                        str(e)
                    ]
                    func_print(out_string)
                else:
                    func_print('Order successfully moved')
            else:
                out_string = [
                    str("An error was encountered processing " + str(blank_summary.loc['Literal Direction'].values[0]) + " " + str(blank_summary.loc['Security'].values[0]) + " on " + str(blank_summary.loc['Exchange'].values[0])),
                    str("Security was ordered at " + str(blank_summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")))
                ]
                func_print(out_string)
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
                    out_string = [
                        str("An error was encountered processing " + str(summary.loc['Literal Direction'].values[0]) + " " + str(summary.loc['Security'].values[0]) + " on " + str(summary.loc['Exchange'].values[0])),
                        str("Security was ordered at " + str(summary.loc['Arrow Order Timestamp'].values[0].format("YYYY-MM-DD HH:mm:ss SSSS ZZ"))),
                        str(e)
                    ]
                    func_print(out_string)
                    for zeta in tracked_serurities_dict:
                        print(tracked_serurities_dict[zeta])
                    print()
                else:
                    open_counter += -1
                    func_print('Order successfully processes')
                    
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
            func_print(str('A failed was encountered writing ' + name + ' to memory.'))
        else:
            pass
    t.end_tracking()
    print()

def time_counter():
    local_time = time.time()
    while True and local_time < start + rts:
        time.sleep(15)
        local_time = time.time()

        

        out_string = [
            str("Time: "+str(int(local_time - start))),
            str('\t'+ 'Blank: '+ str(len(blank_queue))),
            str('\t'+ 'Open: '+ str(len(open_queue))),
            str('\t'+ 'Closed: '+ str(len(closed_queue))),
            str('\t'+ 'Erroneous: '+ str(len(erroneous_orders))),
            str('\t'+ currencies[0] + ": " + str(len(tracked_serurities_dict[currencies[0]]))),
            str('\t'+ currencies[1] + ": " + str(len(tracked_serurities_dict[currencies[1]]))),
            str('\t'+ currencies[2] + ": " + str(len(tracked_serurities_dict[currencies[2]])))
        ]
        func_print(out_string)

def close_position(local_order, open_counter=None):
    action = ph.close_position(local_order)
    if(action):
        closed_queue.append(local_order) #move the position from the open queue to the closed queue
        del open_queue[open_counter]

def algorithm(k_mu = 0.000176971171492904, k_sigma = 0.00625821627270806, stdev_barrier = 1.6, epoch_seconds = 60*29, currencies=currencies, inversion=[False, False, False]):
    time.sleep(int(epoch_seconds))
    position_count = 0
    delay = 5
    while True and time.time() < start + rts:
        time.sleep(int(0 + delay)) #We only really need to update our estimates every 15 seconds, and unlike merely writing to and from memory, this algo will likely be a bit CPU intensive. Maybe.

        #We need to get the last 15 minutes of data for each currency
        pointer_time = ar.utcnow().span('microsecond')[0].to("US/Central").shift(seconds= -1*epoch_seconds)

        operands = {}

        red_flag = False
        for c in currencies:
            try:
                index = tracked_serurities_dict[c].index.where(tracked_serurities_dict[c].index > pointer_time).dropna()
            except:
                red_flag = True
            else:
                if(len(index.values) == 0): 
                    print(index)
                    operands[c] = tracked_serurities_dict[c].loc[index]
        if(not red_flag):
            if(len(operands[currencies[0]]) > 0 and len(operands[currencies[1]]) > 0 and len(operands[currencies[2]]) > 0):

                if(inversion[0]):
                    f = 1/np.mean(operands[currencies[0]]['close'].values)
                else:
                    f = np.mean(operands[currencies[0]]['close'].values)
                
                if(inversion[1]):
                    g = 1/np.mean(operands[currencies[1]]['close'].values)
                else:
                    g = np.mean(operands[currencies[1]]['close'].values)
                
                if(inversion[2]):
                    h = 1/np.mean(operands[currencies[2]]['close'].values)
                else:
                    h = np.mean(operands[currencies[2]]['close'].values)
                
                k = (f/g)-h
                func_print(str("K: " + str(k)))

                z_k = (k-k_mu)/k_sigma
                print(z_k)
                if(np.abs(z_k) > stdev_barrier):#np.abs(z_k) > stdev_barrier
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
                        func_print(str('\t' + "Algorithm has encountered a failure"))
                    else:
                        func_print(str('\t' + "Algorithm has successfully queued " + new_position.information.loc["Literal Direction"][0] + " " + new_position.information.loc["Security"][0] + " on " + new_position.information.loc["Exchange"][0]))

                    delay = int(10)
                else:
                    delay = 0.25
            else:
                pass


    pass

#The purpose of this is to print out every variable so that when we get some fucking error thats in a thread like 3 or 4 divorced from the main,
#we can figure out what the hell went wrong and why
def grand_thread_unfucker():
    pass