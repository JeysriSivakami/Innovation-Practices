import numpy as np
import datetime
from kiteconnect import KiteConnect
from modules import auth
from modules import historical_data
"""
1. Login to Kite
"""
userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])


def calculate_EMA(records, days):
    if days!=9:
        prices = [record['close'] for record in records]
    else:
        prices=records
    smoothing_factor = 2 / (days + 1)
    ema_values = [prices[0]]  # Initialize with the first value
    for i in range(1, len(prices)):
        ema = (prices[i] * smoothing_factor) + (ema_values[-1] * (1 - smoothing_factor))
        ema_values.append(ema)
    return ema_values

def calculate_MACD(records):
    short_period=12
    long_period=26
    signal_period=9
    prices = [record['close'] for record in records]
    short_ema = calculate_EMA(records, short_period)
    long_ema = calculate_EMA(records, long_period)
    macd_line = np.array(short_ema) - np.array(long_ema)
    #print(macd_line)
    signal_line = calculate_EMA(macd_line, signal_period)
    
    if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
        # Buy signal: MACD line crosses above Signal line
        return 1
    elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
        # Sell signal: MACD line crosses below Signal line
        return -1
    else:
        # No signal
        return 0

def calculate_VWAP(records):
    prices = [record['close'] for record in records]
    volumes = [record['volume'] for record in records]
    total_volume = sum(volumes)
    vwap = sum([price * volume for price, volume in zip(prices, volumes)]) / total_volume
    return vwap

def strategy(records,token):
    order_placed = False
    last_order_placed = None
    last_order_price = 0
    profit = 0
    
    for idx, record in enumerate(records):
        #fetch the past 26 hours data from this records

        # Calculate start date (26 hours ago)
        startdate = record['date'] - datetime.timedelta(hours=94)
        
        # End date (current date)
        enddate = record['date']
        # print(startdate)
        # print(enddate)
        # Fetch historical data for the specified token and time range
        prev26recs = kite.historical_data(token, startdate, enddate, "hour")
        #print('length of prev26recs:',len(prev26recs))
        #print(prev26recs)
        ema20 = calculate_EMA(prev26recs, 20)[-1]
        ema5 = calculate_EMA(prev26recs[-5:], 5)[-1]
        pre_ema20=calculate_EMA(prev26recs[-21:-1], 20)[-1]
        pre_ema5 = calculate_EMA(prev26recs[-6:-1], 5)[-1]
        
        macd=calculate_MACD(prev26recs)
        
        vwap=calculate_VWAP(prev26recs[-21:-1])
        #print(vwap)
        #print(record['close'] )
        #print(ema20)
        if (ema5 < ema20) and (pre_ema5 > pre_ema20) and (macd < 0) and (record['close'] < vwap):
            if last_order_placed == "SELL" or last_order_placed is None:
                print("Place a new BUY Order")
                quantity = round(max(1, (2000/record['high'])))
                print('quantity:',quantity)
                print('price:',(record['close']))
                print('total price:',round(record['close']*quantity,2))
                if(last_order_placed==None):
                    print('initial buy:',record['close']*quantity)
                else:
                    profit += (last_order_price - record['close'])*quantity
                last_order_price = record['close']                   
                last_order_placed = "BUY"

        if (ema5 > ema20) and (pre_ema5 > pre_ema20) and (macd > 0) and (record['close'] > vwap):      
            if last_order_placed == "BUY":
				#Calculate Profit again
                quantity = round(max(1, (2000/record['high'])))
                print("Place a new Sell Order")
                print('quantity:',quantity)
                print(record['close'])
                print('total price:',round(record['close']*quantity,2))
                profit += (record['close'] - last_order_price)*quantity
                last_order_price = record['close']
                
                last_order_placed = "SELL"
        if idx == len(records) - 1 and last_order_placed == "BUY":
            profit += record['close'] - last_order_price
            last_order_placed = "SELL"
            print("Place a new Sell Order")
            print(record['close'])
    print("Gross Profit",round(profit,2),"\n\n")
            
def start():
    print("************ Backtesting Started *************")

    startdate = datetime.datetime(2023, 9, 15)
    enddate = datetime.datetime(2023, 12, 30)
    # Define the trading symbol
    symbol = "SILVER"
    symbol_to_token = {
        "SILVER": 2048769,
        # Add more symbols and their corresponding tokens as needed
    }
    token = symbol_to_token.get(symbol)
    if token is None:
        print("Error: Instrument token not found for", symbol)
        exit()
        
    records = kite.historical_data(token, startdate, enddate, "hour")
    
    #print(records)
    strategy(records, token)

start()
