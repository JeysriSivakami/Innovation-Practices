import csv
import re
import pandas as pd
import datetime


def data_collection(startdate,enddate):
    name=file_names()
    df = pd.read_csv(name)
    df['date'] = pd.to_datetime(df['date'])

    # Filter records based on start date and end date
    filtered_df = df[((df['date'].dt.date) >= startdate) & ((df['date'].dt.date) <= enddate)]

    # Convert the filtered DataFrame to a list of dictionaries
    rec = filtered_df.to_dict('records')
    #print(rec) 
    return rec    
 
def strategy(records,token):
    last_order_placed = None
    count=0
    amount=2000
    amt=amount
    for idx, record in enumerate(records):
        startdate = (record['date'] - datetime.timedelta(hours=94)).date()
        enddate = record['date'].date()
        prev26recs=data_collection(startdate,enddate)
        quantity=25
        #ema20 = calculate_EMA(prev26recs, 20)[-1]
        #ema5 = calculate_EMA(prev26recs[-5:], 5)[-1]
        #pre_ema20=calculate_EMA(prev26recs[-21:-1], 20)[-1]
        #pre_ema5 = calculate_EMA(prev26recs[-6:-1], 5)[-1]
        
        #macd=calculate_MACD(prev26recs)
        
        #vwap=calculate_VWAP(prev26recs[-21:-1])
        file_name=file_identify()
        #give your buy condition
        if ((ema5 > ema20) and (pre_ema5 < pre_ema20)) or ((record['close'] > vwap) and (macd < 0)):
            if last_order_placed == "SELL" or last_order_placed is None:
                count+=1
                check=1
                amount -=((record['close'])*quantity)                 
                last_order_placed = "BUY"
        #stop loss of 5 percent is given in selling condition
        #give your buy condition
        elif (((ema5 < ema20) and (pre_ema5 > pre_ema20)) or ((record['close'] < vwap) and (macd > 0))):# or ((record['close']*quantity)<(amount-amount*0.05)):
            if last_order_placed == "BUY":
                amount +=((record['close'])*quantity)
                count+=1
                check=1
                last_order_placed = "SELL"
        if idx == len(records) - 1 and last_order_placed == "BUY":
            amount +=((record['close'])*quantity)
            last_order_placed = "SELL"
            count+=1
            check=1
        row=[count,last_order_placed,record['date'],round(record['close']*quantity,2),round(ema5,2),round(ema20,2),round(vwap,2),round(macd,2)]
        if(check==1):
            with open(file_name, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(row)
    print("Total Buy and Sell:",count/2,"Amount at last is:",round(amount,2),"\n\n")
    print('profit: ',round(amount-amt,2))
    profit_percent = ((amount - amt) / amt) * 100
    print('profit percent: ', round(profit_percent,2))
    row1=['profit_percent', 'profit']
    row2=[round(profit_percent,2),round(amount-amt,2)]
    with open(file_name, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row1)
            csvwriter.writerow(row2)

def file_names():
    inter='hour'
    filename = '2023 ' +inter+'.csv'
    return filename

def file_identify():
    filename = '2023 hour'
    strategy_no=' strategy1 year';
    file_name=filename+ strategy_no+' results'+'.csv'
    return file_name

def read_records(startdate, enddate):
    # Read the CSV file into a DataFrame
    filename=file_names()
    df = pd.read_csv(filename)
    file_name=file_identify()
    with open(file_name, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['interval'])
        csvwriter.writerow([re.split(r'\.(?=[^.])', filename)])
        csvwriter.writerow(['transaction_no', 'buy/sell', 'date','price', 'ema5','ema20','vwap','macd'])
    df['date'] = pd.to_datetime(df['date'])

    # Filter records based on start date and end date
    filtered_df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]

    # Convert the filtered DataFrame to a list of dictionaries
    rec = filtered_df.to_dict('records')
    #print(rec) 
    return rec  

def start():
    print("************ Backtesting Started *************")

    startdate =  datetime.datetime(2023, 2, 2, 9, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    enddate =  datetime.datetime(2023, 12, 1, 15, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))

    
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
    records=read_records(startdate,enddate)
    strategy(records, token)

start()
