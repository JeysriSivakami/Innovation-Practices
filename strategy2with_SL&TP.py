import numpy as np
import datetime
from kiteconnect import KiteConnect
from modules import auth
from modules import historical_data
import pandas as pd
import matplotlib.pyplot as plt

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
def graph(transactions,portfolio_values):
    plt.plot(transactions, portfolio_values, marker='o')
    # Adding labels and title
    plt.xlabel('Transactions')
    plt.ylabel('Portfolio Value')
    plt.title('Portfolio Performance Over Time')
    
    # Rotating x-axis labels for better readability
    plt.xticks(rotation=45)

    # Displaying the graph
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.show()

def strategy(records,token):
    order_placed = False
    last_order_placed = None
    last_order_price = 0
    profit = 0
    portfolio=2000
    stop_loss=100
    take_profit=100
    transaction=0
    transac_date=[]
    portfolio_val=[]
    for idx, record in enumerate(records):
        #fetch the past 26 hours data from this records
        # Calculate start date (26 hours ago)
        startdate = record['date'] - datetime.timedelta(hours=94)
        enddate = record['date']
        
        prev26recs = read_records( startdate, enddate)
        ema20 = calculate_EMA(prev26recs, 20)[-1]
        ema5 = calculate_EMA(prev26recs[-5:], 5)[-1]
        pre_ema20=calculate_EMA(prev26recs[-21:-1], 20)[-1]
        pre_ema5 = calculate_EMA(prev26recs[-6:-1], 5)[-1]
        
        macd=calculate_MACD(prev26recs)
        
        vwap=calculate_VWAP(prev26recs[-25:])

        if  (ema5 > ema20 and pre_ema5 < pre_ema20)  or ((macd < 0) and (record['close']> vwap)):
            if last_order_placed == "SELL" or last_order_placed is None:
                print("Place a new BUY Order")
                quantity = 27
                print('price:',(record['close']))
                portfolio-=record['close']*quantity 
                last_order_price = record['close']                 
                last_order_placed = "BUY"
        if last_order_placed == "BUY":
            current_price = record['close']
            if last_order_price*quantity-current_price*quantity >= stop_loss:
                # Sell due to stop loss
                print("Place a new Sell Order (Stop Loss Hit)")
                portfolio += current_price * quantity
                print(portfolio)
                last_order_placed = "SELL"
                transaction += 1

            elif current_price*quantity - last_order_price*quantity >= take_profit:
                # Sell due to take profit
                print("Place a new Sell Order (Take Profit Hit)")
                portfolio += current_price * quantity
                print(portfolio)
                last_order_placed = "SELL"
                transaction += 1

        if (ema5 < ema20 and pre_ema5 > pre_ema20)  or ((macd > 0) and (record['close'] < vwap))  :   
            if last_order_placed == "BUY":
				#Calculate Profit again
                quantity = 27
                print("Place a new Sell Order")
                print(record['close'])
                portfolio+=record['close']*quantity   
                print(portfolio)                           
                last_order_placed = "SELL"
                transaction+=1
                transac_date.append(record['date'].date())
                portfolio_val.append(portfolio)

        if idx == len(records) - 1 and last_order_placed == "BUY":
            profit += record['close'] - last_order_price
            last_order_placed = "SELL"
            print(record['close'])
            print("Place a new Sell Order")
            portfolio+=record['close']*quantity
            transaction+=1
            transac_date.append(record['date'].date())
            portfolio_val.append(portfolio)
    print("************ Results *************")
    print('stop loss:',stop_loss)
    print('take profit:',take_profit)
    print('transactions:',transaction)
    print("Profit",portfolio-2000)
    print('portfolio:',portfolio)
    print('profit percent:',portfolio-2000/portfolio)
    graph(transac_date,portfolio_val)
def read_records(startdate, enddate):
    # Read the CSV file into a DataFrame
    df = pd.read_csv('2023.csv')

    # Convert the 'date' column to datetime type
    df['date'] = pd.to_datetime(df['date'])

    # Filter records based on start date and end date
    filtered_df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]

    # Convert the filtered DataFrame to a list of dictionaries
    records = filtered_df.to_dict('records')

    return records 
      
def start():
    print("************ Backtesting Started *************")

    startdate =  datetime.datetime(2023, 2, 2, 9, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    enddate =  datetime.datetime(2023, 12, 1, 15, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    # Define the trading symbol
    token=2048769
        
    records =  read_records(startdate, enddate)
    
    #print(records)
    strategy(records, token)

start()
