#this is going to be an almost pure math algorithm lib....
#Don't expect many supporting functions, libraries really except for numpy
#Every algorithm should output buy or hold or sell

import numpy as np

def conservation_algo(quote_a, quote_b, quote_c, invert_a = False, invert_b = False, invert_c = False):
    
    if(invert_a):
        quote_a = 1/quote_a
    if(invert_b):
        quote_b = 1/quote_b
    if(invert_c):
        quote_c = 1/quote_c
    
    if(len(quote_a) == len(quote_b) == len(quote_c)):
        k = np.sum((quote_a / quote_b) - quote_c)
        return k
    else:
        return None

def conservation_algo_improved_15_epoch(quote_a, quote_b, quote_c, invert_a = False, invert_b = False, invert_c = False, stdev_boundary = 0, stdev = 1, mu = 0):
    if(invert_a):
        quote_a = 1/quote_a
    if(invert_b):
        quote_b = 1/quote_b
    if(invert_c):
        quote_c = 1/quote_c
    
    if(len(quote_a) == len(quote_b) == len(quote_c)):
        k = np.sum((quote_a / quote_b) - quote_c)
    else:
        return None
    
    z = (k - mu)/stdev
    
    if(np.abs(z) > stdev_boundary):
        return k
    else:
        return 0