import pandas as pd 
import arrow as ar
import numpy as np

class position:
    def __init__(self, exchange, security, size, direction, k_purchase, est_maturity_time=8, terminal_time=15, order_ts=ar.utcnow().span('microsecond')[0].to("US/Central"), price='market'):        
        if(direction == np.float64(1)):
            literal_direction = "long"
        elif(direction == np.float64(-1)):
            literal_direction = "short"
        
        d = {
            "Exchange" : exchange,
            "Security" : security,
            "Execution Price" : None,
            "Size" : np.float64(size),
            "Direction" : np.float64(direction),
            "Literal Direction" : literal_direction,
            "Arrow Order Timestamp" : order_ts,
            "Arrow Estimated Maturity Timestamp" : order_ts.shift(minutes= est_maturity_time),
            "Arrow Terminal Time" : order_ts.shift(minutes= terminal_time),
            "Arrow Position Filled TS" : None,
            "Arrow Position Closed TS" : None,
            "k_purchase" : k_purchase,
            'filled' : False,
            'closed' : False,
            'net fees' : 0,
            'Sale Price' : None,
            'terminal time' : terminal_time
        }

        d["Order Timestamp"] = d['Arrow Order Timestamp'].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")
        d['Estimated Maturity Timestamp'] = d['Arrow Estimated Maturity Timestamp'].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")
        d['Terminal Timestamp'] = d['Arrow Terminal Time'].format("YYYY-MM-DD HH:mm:ss SSSS ZZ")

        df = pd.DataFrame(d, index=["Parameters"]).T
        self.information = df

        self.compute_summary()

    def compute_summary(self):
        return self.information.drop(['Direction', 'Arrow Order Timestamp', 'Arrow Estimated Maturity Timestamp', 'Arrow Terminal Time'])

    def summary(self):
        return self.compute_summary()
    
    def info(self):
        return self.information

