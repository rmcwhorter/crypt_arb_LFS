print("SOF")
import currency_pairs
import pandas as pd 
import numpy as np 
import websocket
import json
import time
import arrow
import threading
import pickle

import currency_pairs

with open("data/data_parsed/parsed.pkl", "rb") as handle: parsed_frame = pickle.load(handle)

for col in parsed_frame.columns.values[1:]:
    parsed_frame[col] = list(map(lambda x: float(x), parsed_frame[col].values))


literal_currency = []
for c in parsed_frame['currency_pair_id'].values:
    literal_currency.append(currency_pairs.inv_currency_pairs[c])

parsed_frame['literal_pair'] = literal_currency

parsed_frame['near_term_high_low_spread'] = parsed_frame['lowest_ask'] - parsed_frame['highest_bid'] #if this is positive, then no one is willing to buy for the given price, if this is negative, then the market should have people exchanging shares.
parsed_frame['near_term_last_high_spread'] = parsed_frame['last_trade_price'] - parsed_frame['highest_bid'] #if this is positive, then no one is willing to buy for the same price that the last share was sold for, we might surmise that the price is going down
parsed_frame['near_term_last_low_spread'] = parsed_frame['lowest_ask'] - parsed_frame['last_trade_price'] #if this is positive, then no one is willing to sell for the same price as the last trade, and we might surmise that the price is going up.
parsed_frame['near_term_last_prop_spread'] = (parsed_frame['last_trade_price'] - parsed_frame['highest_bid'])/(parsed_frame['lowest_ask'] - parsed_frame['highest_bid']) #This should* be a measure of where the coin is trading between the bid and ask prices. This might give an estimation of where things are headed. 
parsed_frame['24_hr_spread'] = parsed_frame['24_hr_high'] - parsed_frame['24_hr_low']
parsed_frame['24_hr_spread_prop'] = (parsed_frame['last_trade_price'] - parsed_frame['24_hr_low']) / (parsed_frame['24_hr_spread'])

print(parsed_frame.columns.values)
print(parsed_frame)

print(f"{max(parsed_frame['near_term_last_prop_spread'])} {min(parsed_frame['near_term_last_prop_spread'])} {np.median(parsed_frame['near_term_last_prop_spread'])}")

out = []
for a in parsed_frame.columns:
    out = out + list(map(lambda x: x == np.nan,parsed_frame[col].values))

print(parsed_frame.loc[parsed_frame['currency_pair_id'] == 50])

print("EOF")