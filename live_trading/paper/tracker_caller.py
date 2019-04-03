import sys
import tracker

ticker = sys.argv[1]
exchange = sys.argv[2]

print(sys.argv)

asdf = "asdf_" + ticker

tracker.tracker(exchange, ticker)

