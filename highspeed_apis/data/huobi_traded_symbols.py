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
import requests

s = requests.get(url = 'https://api.huobi.com/v1/common/symbols').json()

for a in s['data']:
    print(a['base-currency'],a['quote-currency'])

print("EOF")