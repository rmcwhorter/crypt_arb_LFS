import trading_desk as td
import arrow as ar

#What we want to happen:
#The algorithm notices that we should take a long position
#The algorithm creates a blank position
#That position is queued in an array of unfilled orders
#A function is called on each order, from oldest order to newest
#That function takes the order and fills it at market price

def close_position(position):
    #We close positions at their book value less net fees
    summary = position.information


    if(summary.loc["Literal Direction"][0] == 'long'):
        order = td.short(summary.loc['Exchange'][0], summary.loc['Security'][0], summary.loc['Size'][0] - summary.loc['net fees'][0])

        if(order[0]):
            summary.loc['net fees'][0] += order[1]
            summary.loc['closed'][0] = True
            summary.loc['Sale Price'][0] = order[2]
            summary.loc['Arrow Position Closed TS'] = ar.utcnow().span('microsecond')[0].to("US/Central")

            return True
        else:
            return False


    elif(position.summary().loc["Literal Direction"][0] == 'short'):
        order = td.long(summary.loc['Exchange'][0], summary.loc['Security'][0], summary.loc['Size'][0] + summary.loc['net fees'][0])

        if(order[0]):
            summary.loc['net fees'][0] += order[1]
            summary.loc['closed'][0] = True
            summary.loc['Sale Price'][0] = order[2]
            summary.loc['Arrow Position Closed TS'] = ar.utcnow().span('microsecond')[0].to("US/Central")

            return True
        else:
            return False

def open_position(position):
    #We close positions at their book value less net fees
    summary = position.information


    if(summary.loc["Literal Direction"][0] == 'short'):
        order = td.short(summary.loc['Exchange'][0], summary.loc['Security'][0], summary.loc['Size'][0] - summary.loc['net fees'][0])

        if(order[0]):
            summary.loc['net fees'][0] += order[1]
            summary.loc['filled'][0] = True
            summary.loc['Execution Price'][0] = order[2]
            summary.loc['Arrow Position Filled TS'][0] = ar.utcnow().span('microsecond')[0].to("US/Central")
            summary.loc['Arrow Terminal Time'][0] = summary.loc['Arrow Position Filled TS'][0].shift(minutes= summary.loc['terminal time'][0])

            return True
        else:
            return False


    elif(position.summary().loc["Literal Direction"][0] == 'long'):
        order = td.long(summary.loc['Exchange'][0], summary.loc['Security'][0], summary.loc['Size'][0] + summary.loc['net fees'][0])

        if(order[0]):
            summary.loc['net fees'][0] += order[1]
            summary.loc['filled'][0] = True
            summary.loc['Execution Price'][0] = order[2]
            summary.loc['Arrow Position Filled TS'][0] = ar.utcnow().span('microsecond')[0].to("US/Central")
            summary.loc['Arrow Terminal Time'][0] = summary.loc['Arrow Position Filled TS'][0].shift(minutes= summary.loc['terminal time'][0])

            return True
        else:
            return False
