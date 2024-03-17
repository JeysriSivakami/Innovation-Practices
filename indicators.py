import datetime
from kiteconnect import KiteConnect
from modules import auth
from modules import historical_data
import pandas as pd

"""
1. Login to kite
"""
userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

print("******** UserData Loaded ********* : ", datetime.datetime.now())


interval = "10minute"


tickerlist = ["BANKNIFTY20MAYFUT"]
tokenlist = [13430018]


def check_volume(open, volume):
    if open <= 400 and volume >= 1000000:
        return True
    elif open > 400 and open <=700 and volume >= 500000:
        return True
    elif open > 700 and open <=1000 and volume >= 300000:
        return True
    elif open > 1000 and volume >= 100000:
        return True
    else:
        return False

def strategy(records, token):
    order_placed = False
    last_order_placed = None
    last_order_price = 0
    profit = 0
    
    
    
    for record in records:

        enddate = datetime.strptime(record['timestamp'], "%Y-%m-%d %H:%M:%S%z")
        startdate = enddate - datetime.timedelta(15)
        df = historical_data.get(kite, token, startdate, enddate, "60minute")
        df = EMA.calc(df,'close','ema_5',5)
        df = EMA.calc(df,'close','ema_20',20)
        df = MACD.calc(df)
        df = MFI.calc(df)
        df = VWAP.calc(df)
        rsi = historical_data.get(kite, token, startdate, enddate, "60minute")
        rsi = RSI.calc(rsi)
        one_hour_rsi = rsi.RSI_14.values[-2]
        #print(record)
        pre_ema5 = df.ema_5.values[-3]
        pre_ema20 = df.ema_20.values[-3]
        pre_close = df.close.values[-3]
        
        ema5 = df.ema_5.values[-2]
        ema20 = df.ema_20.values[-2]
        macd = df.hist_12_26_9.values[-2]
        mfi = df.mfi.values[-2]
        vwap = df.vwap.values[-2]
        
        open = df.open.values[-2]
        close = df.close.values[-2]
        high = df.high.values[-2]
        low = df.low.values[-2]
        
        volume = df.volume.values[-2]
        has_volume = check_volume(histdata.open.values[-2], volume)

        perc_change = ((close - pre_close) * 100) / open
        
        if (ema5 > ema20) and (pre_ema5 < pre_ema20) and (macd > 0) and (close > vwap):
                if not has_volume:
                    print("Sorry, Volume is low")
                    #continue
                
                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (2500/high)))

                profit -= record['close']*quantity
                
        if (ema5 < ema20) and (pre_ema5 > pre_ema20) and (macd < 0) and (close < vwap):
                if not has_volume:
                    print("Sorry, Volume is low")
                    #continue

                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (2500/high)))
                
                profit += record['close']*quantity
                
    print("Gross Profit",profit,"\n\n")

def start():
    print("************ Backtesting Started *************")
    for i in range(0, len(tickerlist)):
        
        
        #startdate = enddate - datetime.timedelta(1)
        startdate = datetime.datetime(2020, 3, 15)
        enddate = datetime.datetime(2020, 10, 15)
        #enddate = datetime.datetime.today()

        print(interval)
        records = kite.historical_data(tokenlist[i], startdate, enddate, interval)

        #print("\n\n", records)

        #historical_data.get(kite, tokenlist[i], startdate, enddate, interval)
        print("\n************* ", tickerlist[i], "************")
        strategy(records, tokenlist[i])

start()

