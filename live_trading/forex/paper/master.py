import ondemand
import pandas as pd
import numpy as np

local_key = "b5d3e28278677c90676420e5ef91aa39"

od = ondemand.OnDemandClient(api_key=local_key)

# or if you are using a free sandbox API

od = ondemand.OnDemandClient(api_key=local_key, end_point='https://marketdata.websol.barchart.com/')

# get quote data for Apple and Microsoft
quotes = od.quote('^usdaud')['results']

for q in quotes:
    print('Symbol: %s, Last Price: %s' % (q['symbol'], q['lastPrice']))

# get 1 minutes bars for Apple
resp = od.history('^usdaud', 'minutes', maxRecords=1000, interval=1)

print(type(resp))
#print(res
#p['results'])
print(resp)

def parse_to_pandas(results):
    cols = list(results[0].keys())
    blank = pd.DataFrame(results[0], columns=cols, index=[results[0]['timestamp']])

    for tick in results[1:]:
        blank = blank.append((pd.DataFrame(tick, columns=cols, index=[tick['timestamp']])))#.drop(columns=['timestamp'])

    return blank.drop(columns=['timestamp'])

#print(parse_to_pandas(resp['results']))
