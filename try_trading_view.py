import numpy as np
import datetime
from kiteconnect import KiteConnect
from modules import auth
from modules import historical_data
import pandas as pd
import matplotlib.pyplot as plt

def graph(transactions,portfolio_values):
    plt.plot(transactions, portfolio_values, marker='o')
    plt.xlabel('Transactions')
    plt.ylabel('Portfolio Value')
    plt.title('Portfolio Performance Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
#implement your strategy
def strategy(records):
    order_placed = False
    last_order_placed = None
    last_order_price = 0
    portfolio=2000
    stop_loss=100
    take_profit=100
    transaction=0
    transac_date=[]
    portfolio_val=[]
    for idx, record in enumerate(records):
        if  (#give buy condition here):
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
                print("Place a new Sell Order (Stop Loss Hit)")
                portfolio += current_price * quantity
                print(portfolio)
                last_order_placed = "SELL"
                transaction += 1

            elif current_price*quantity - last_order_price*quantity >= take_profit:
                print("Place a new Sell Order (Take Profit Hit)")
                portfolio += current_price * quantity
                print(portfolio)
                last_order_placed = "SELL"
                transaction += 1

        if (#give sell condition here)  :   
            if last_order_placed == "BUY":
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
    print('profit percent:',((portfolio-2000)/portfolio)*100)
    graph(transac_date,portfolio_val)

def read_records(startdate, enddate):
    df = pd.read_csv('2023.csv')
    df['date'] = pd.to_datetime(df['date'])
    filtered_df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]
    records = filtered_df.to_dict('records')
    return records 
      
def start():
    print("************ Backtesting Started *************")

    startdate =  datetime.datetime(2023, 1, 6, 9, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    enddate =  datetime.datetime(2023, 12, 1, 15, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        
    records =  read_records(startdate, enddate)
    strategy(records)

start()
