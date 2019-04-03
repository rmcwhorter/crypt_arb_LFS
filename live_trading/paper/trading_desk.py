import lib

def short(exchange, security, size, price='market'):
    pass
    #This needs to return true if the order is successfully executed
    #This also needs to return net fees incurred
    #This also needs to return the price the order was filled at
    fees = 0
    
    l = len(lib.tracked_serurities_dict[security])
    fill_price = lib.tracked_serurities_dict[security].iloc[l-1]['close']
    print("Short ",security, " @ ", fill_price)

    return (True, fees, fill_price)

def long(exchange, security, size, price='market'):
    pass
    #This needs to return true if the order is successfully executed
    #This also needs to return net fees incurred
    #This also needs to return the price the order was filled at
    fees = 0
    l = len(lib.tracked_serurities_dict[security])
    fill_price = lib.tracked_serurities_dict[security].iloc[l-1]['close']
    print("Long ",security, " @ ", fill_price)

    return (True, fees, fill_price)