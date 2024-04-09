import numpy as np
import datetime
from kiteconnect import KiteConnect
from modules import auth
from modules import historical_data
import pandas as pd
import matplotlib.pyplot as plt
import csv
import re

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

def strategy(records):
    check=0
    bcount=0
    scount=0
    bars=10
    last_order_placed = None
    days = 20
    ma = 0
    sum=0
    amount=1000000
    portfolio=amount
    stop_loss=50000
    take_profit=10000
    transaction=0
    transac_date=[]
    portfolio_val=[]
    quantity = 10
    for idx, record in enumerate(records):
        if idx<days:
            sum+=record['close']
            continue
        ma=sum/days
        sum-=records[idx-days]['close']
        sum+=record['close']
        if record['close']>ma:
            bcount+=1
        else:
            bcount=0
        if record['close']<ma:
            scount+=1
        else:
            scount=0
        if bcount>=bars and (last_order_placed == "SELL" or last_order_placed is None) and record['date'].time() <= datetime.time(22, 59):
            print("Place a new BUY Order")
            print('price:',(record['close']))
            portfolio-=record['close']*quantity 
            last_order_price = record['close']                 
            last_order_placed = "BUY"
            transaction += 1
            check=1
        elif last_order_placed == "BUY":
            current_price = record['close']
            if  record['date'].time() >= datetime.time(22, 59):
                print("Place a new Sell Order (Intraday hit)")
                portfolio += current_price * quantity
                print(portfolio)
                last_order_placed = "SELL"
                transaction += 1
                check=1
            elif (last_order_price*quantity)-(current_price*quantity) >= stop_loss:
                # Sell due to stop loss
                print("Place a new Sell Order (Stop Loss Hit)")
                portfolio += current_price * quantity
                print(portfolio)
                last_order_placed = "SELL"
                transaction += 1
                check=1

            elif current_price*quantity - last_order_price*quantity >= take_profit:
                # Sell due to take profit
                print("Place a new Sell Order (Take Profit Hit)")
                portfolio += current_price * quantity
                print(portfolio)
                last_order_placed = "SELL"
                transaction += 1
                check=1
            elif idx == len(records) - 1:
                last_order_placed = "SELL"
                print(record['close'])
                print("Place a new Sell Order(end of records hit)")
                portfolio+=record['close']*quantity
                transaction+=1
                check=1
                transac_date.append(record['date'].date())
                portfolio_val.append(portfolio)
            elif scount>=bars:   
                #Calculate Profit again
                print("Place a new Sell Order(condition hit)")
                print(record['close'])
                portfolio+=record['close']*quantity   
                print(portfolio)                           
                last_order_placed = "SELL"
                transaction+=1
                transac_date.append(record['date'].date())
                portfolio_val.append(portfolio)
                check=1
        if(check==1):
            print("transac",transaction)
            print("port",portfolio)
            row=[transaction,last_order_placed,record['date'],round(record['close']*quantity,2)]
            with open("silver_micro_backtest.csv", 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(row)
        check =0
    print("************ Results *************")
    #print('bars:',bars,' avg days:',days)
    #print('stop loss:',stop_loss)
   # print('take profit:',take_profit)
    print('transactions:',transaction/2)
    print("port",portfolio)
    print("amt",amount)
    print("Profit",portfolio-amount)
    print('portfolio:',portfolio)
    profit_percent = ((portfolio - amount) / amount) * 100
    print('profit percent: ', round(profit_percent,2))
    row1=['profit_percent', 'profit']
    row2=[round(profit_percent,2),round(portfolio - amount,2)]
    with open("silver_micro_backtest.csv", 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row1)
            csvwriter.writerow(row2)
    graph(transac_date,portfolio_val)
def read_records(startdate, enddate):
    filename="silver_micro_backtest.csv"
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['transaction_no', 'buy/sell', 'date','price'])
    df = pd.read_csv('micro_15.csv')
    df['date'] = pd.to_datetime(df['date'])
    filtered_df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]
    records = filtered_df.to_dict('records')
    return records 
      
def start():
    print("************ Backtesting Started *************")

    startdate =  datetime.datetime(2023, 12, 14, 17, 00, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    enddate =  datetime.datetime(2024, 4, 4, 23, 00, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        
    records =  read_records(startdate, enddate)
    
    #print(records)
    strategy(records)

start()